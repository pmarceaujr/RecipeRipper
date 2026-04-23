import requests
from bs4 import BeautifulSoup
import openai
import os
import json
import re
import base64
import time
from PyPDF2 import PdfReader
from PIL import Image
import io
import boto3
from botocore.exceptions import ClientError
from flask import current_app
import logging

logger = logging.getLogger(__name__)

# AWS Credentials
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")
S3_BUCKET = os.getenv("S3_BUCKET")

# OpenAI API KEY
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = os.getenv('OPENAI_API_KEY')
if not openai.api_key:
    logger.info("Warning: OPENAI_API_KEY is not set in environment variables.")
else:
    logger.info(f"OPENAI_API_KEY found: ...{openai.api_key[-10:]}")  # Print first 10 chars for verification

# Initialize AWS clients
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION
)
textract = boto3.client(
    "textract",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION
)

def scrape_url(url):
    logger.info("Scraping URL...")
    """Scrape recipe content from a URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            element.decompose()
        
        # Get text content
        text = soup.get_text(separator='\n', strip=True)
        # print(f"Scraped text: {text}")  # Debugging line
        
        # Clean up excessive whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text[:15000]  # Limit to 15k chars to avoid token limits
    except Exception as e:
        raise Exception(f"Failed to scrape URL: {str(e)}")

def extract_text_from_pdf(file_path, filename):
    logger.info("Initializing PDF text extraction...")
    """Extract text from PDF file"""
    try:
        # Check if PDF has embedded text
        reader = PdfReader(file_path)        
        if any(page.extract_text() for page in reader.pages):
            logger.info("Text-based PDF detected")
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        else:
            logger.info("Scanned PDF detected — running Textract OCR")
            # Upload PDF to S3
            s3.upload_file(str(file_path), S3_BUCKET, filename)
            # Call Textract
            # Start asynchronous job
            response = textract.start_document_text_detection(
                DocumentLocation={'S3Object': {'Bucket': S3_BUCKET, 'Name': filename}}
            )
            textract_job_id = response['JobId']

            # Wait for job to complete (simple polling - improve with SNS/SQS for production)
            while True:
                status = textract.get_document_text_detection(JobId=textract_job_id)
                job_status = status['JobStatus']

                if job_status in ['SUCCEEDED', 'FAILED']:
                    break
                time.sleep(5)  # Poll every 5 seconds

            if job_status == 'FAILED':
                raise Exception(f"Textract job failed: {status.get('StatusMessage')}")

            # Extract text from all pages
            full_text = []
            for block in status.get('Blocks', []):
                if block['BlockType'] == 'LINE':
                    full_text.append(block['Text'])

            return "\n".join(full_text)

    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise Exception(f"Failed to extract text from PDF: {str(e)}")

def extract_text_from_image(file_path):
    logger.info("Initializing image text extraction...")
    """Extract text from image using OpenAI Vision API"""
    try:
        # Read and encode image
        with open(file_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Determine image type
        image_extension = os.path.splitext(file_path)[1].lower()
        mime_type = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png'
        }.get(image_extension, 'image/jpeg')
        
        # Use OpenAI Vision to extract text
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract all text from this recipe image. Include the recipe title, all ingredients with measurements, and all cooking directions. Return the raw text exactly as it appears."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=2000
        )

        return response.choices[0].message.content
        
    except Exception as e:
        raise Exception(f"Failed to extract text from image: {str(e)}")


def parse_recipe_text(text, recipe_source=None, is_file=True):
    logger.info("Parsing recipe text...")  # Debugging line
    """Use OpenAI to parse recipe text into structured format"""
    try:
        prompt = f"""Extract recipe information from the following text and return ONLY valid JSON with this exact structure
        (no markdown, no code blocks, just raw JSON).

        IMPORTANT:
        - Ingredients MUST be extracted verbatim as they appear in the text, but parsed correctly according to rules below.
        - Directions MUST be rewritten into neutral, functional cooking steps.
        - Do NOT copy phrasing from the original directions.
        - Do NOT use expressive, descriptive, or narrative language in directions.
        - Preserve cooking order, timing, temperatures, and techniques exactly.
        - Use short, clear, instructional sentences.

        JSON STRUCTURE (EXACT):
        {{
        "title": "recipe name",
        "course": "one category: Breakfast, Lunch, Dinner, Dessert, Appetizer, Snack, Beverage, or Baking",
        "cuisine": "one category: American, Italian, Mexican, Chinese, Indian, French, German, Japanese, Thai, or Other",
        "prep_time": "time in minutes",
        "cook_time": "time in minutes",
        "total_time": "time in minutes",
        "servings": "number of servings",
        "primary_ingredient": "one choice: Beef, Chicken, Pork, Vegetables, Fish, Dairy, Grains, Pasta, Lamb, Venison, Bear, Moose, or Other",
        "ingredients": [
            {{"ingredient": "all-purpose flour", "quantity": "2", "unit": "cups"}},
            {{"ingredient": "granulated sugar", "quantity": "1", "unit": "cup"}},
            {{"ingredient": "large eggs", "quantity": "3", "unit": ""}},
            {{"ingredient": "tomato sauce", "quantity": "2", "unit": "cans"}},
            {{"ingredient": "vanilla extract", "quantity": "1", "unit": "tsp"}}
            {{"ingredient": "fresh basil leaves, roughly chopped", "quantity": "1", "unit": "handful"}}
        ],
        "directions": [
            {{"step_number": 1, "instruction": "Preheat oven to 350°F"}},
            {{"step_number": 2, "instruction": "Mix dry ingredients in a bowl"}}
        ],
        "comments": []
        }}

        DIRECTION REWRITE RULES (MANDATORY):
        - Rewrite EVERY step; do NOT summarize or omit steps.
        - Do NOT reuse sentence structure or phrasing from the source.
        - Replace descriptive language with functional equivalents.
        - Output numbered steps starting at 1.
        - Do NOT mention the original source.
        - Do NOT add or remove ingredients or steps.

        UNIT NORMALIZATION (MANDATORY):
        All ingredient units MUST be converted to one of the following standard abbreviations.
        If the source text uses ANY other wording, convert it using this table.

        - teaspoon, teaspoons, tsp., tsps → "tsp"
        - tablespoon, tablespoons, tbsp., tbsps → "tbsp"
        - cup, cups → "cup" or "cups" (keep plural when appropriate)
        - can, cans → "can" or "cans"
        - ounce, ounces, oz., ozs → "oz"
        - pound, pounds, lb., lbs → "lb"
        - gram, grams, g → "g"
        - kilogram, kilograms, kg → "kg"
        - milliliter, milliliters, ml → "ml"
        - liter, liters, l → "l"
        - pinch, pinches → "pinch"
        - dash, dashes → "dash"
        - clove, cloves → "clove"

        ❗ DO NOT output full unit words (e.g., "teaspoon", "tablespoon").
        ❗ DO NOT invent units.
        ❗ If no unit is provided in the text, use an empty string "".

        CONTAINER/PACKAGE PARSING RULES (MANDATORY - CRITICAL FOR CANS):
        Handle can sizes and packaged items intelligently:

        Common patterns and correct parsing:

        - "28 oz can tomatoes" / "28 ounce can" / "28-oz can of tomato sauce"  
        → quantity="28", unit="oz", ingredient="tomatoes" (or "tomato sauce")

        - "28-ounce can tomatoes" / "28-ounce can" / "28-oz can of tomato sauce"  
        → quantity="28", unit="oz", ingredient="tomatoes" (or "tomato sauce")        

        - "2 (28 oz) cans crushed tomatoes" / "two 28 ounce cans"  
        → quantity="2", unit="cans", ingredient="crushed tomatoes"  
        → Alternative (cleaner): quantity="2", unit="cans", ingredient="crushed tomatoes (28 oz each)"

        - "2 cans (one 28 ounces, one 14-1/2 ounces) stewed tomatoes" / "two 28 oz cans of stewed tomatoes"
        → quantity="2", unit="cans", ingredient="stewed tomatoes (one 28 oz, one 14.5 oz)"

        - "2 cans (8 ounces each) tomato sauce" / "two 8 oz cans of tomato sauce"  
        → quantity="2", unit="cans", ingredient="tomato sauce (8 oz)

        - "1 can (16 ounces) kidney beans" / "one 16 oz can kidney beans"
        → quantity="1", unit="can", ingredient="kidney beans (16 oz)"

        - "one 15 ounce can black beans" / "1 8 oz can"  
        → quantity="1", unit="can", ingredient="black beans (15 oz)"

        - "8 oz can tomato paste" (no number before "8 oz")  
        → quantity="1", unit="can", ingredient="tomato paste (8 oz)"  
        or quantity="8", unit="oz", ingredient="tomato paste"

        Preferred style: 
        - If there's a clear count of containers (2 cans, three 28 oz cans, etc.) → use quantity as the number of cans, unit="can" or "cans", put size in ingredient name.
        - If it's just "28 oz can" with no separate count → use quantity="28", unit="oz", ingredient="..." (most useful for shopping/scaling).

        NEVER put "can", "oz", or "ounce" into the unit field if it's describing container size — unit must come only from the normalization table.

        After applying these rules, ALWAYS verify that every .unit is one of: tsp, tbsp, cup, cups, can, cans, oz, lb, g, kg, ml, l, pinch, dash, clove, or "".

        CRITICAL INGREDIENT RULES:
        1. Extract ALL ingredients — do not skip any.
        2. Parse quantities carefully: "1 tablespoon" → quantity="1", unit="tbsp".
        3. Keep descriptors with the ingredient name: "large sweet potatoes", "drained", "cut into 1/2 inch slices", "roughly chopped".
        4. If an ingredient has no quantity or unit, set them to empty string "".
        5. Units MUST strictly follow the Unit Normalization table + container rules.
        6. Preserve preparation notes in the ingredient name: "peeled and diced".
        7. Return ONLY the JSON object — no explanations, no markdown.

        FINAL VALIDATION RULE:
        Before returning the JSON, verify that EVERY ingredient.unit value is either:
        - one of the allowed abbreviations, or
        - an empty string "".
        If not, correct it.

        Text:
        {text}
        """        
       

        logger.info("Prompt complete")  # Debugging line
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # Fast and accurate - or use "gpt-4o" for best results
            messages=[
                {"role": "system", "content": "You are a precise recipe parser. Extract ALL ingredients without skipping any. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Lower temperature = more consistent
            max_tokens=3000
        )

        content = response.choices[0].message.content.strip()
        # Remove markdown code blocks if present
        content = re.sub(r'^```json\s*|\s*```$', '', content, flags=re.MULTILINE)
        content = content.strip()
        
        # Parse JSON
        recipe_data = json.loads(content)
        
        # Add source URL if provided
        if recipe_source:
            recipe_data['recipe_source'] = recipe_source

        # Add source type (file or URL)
        if is_file:
            recipe_data['is_url'] = 1
        else:
            recipe_data['is_url'] = 0
        
        return recipe_data
        
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse AI response as JSON: {str(e)}\nResponse: {content}")
    except Exception as e:
        raise Exception(f"Failed to parse recipe: {str(e)}")

def parse_from_file(file_path, filename=None):
    """
    Reads the entire content of a text file and returns it as a string.
    
    :param filename: Path to the .txt file
    :return: String containing the file content
    :raises FileNotFoundError: If the file does not exist
    :raises IOError: If there is an error reading the file
    """
    try:
        # Open the file in read mode with UTF-8 encoding
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        raise
    except IOError as e:
        print(f"Error reading file '{file_path}': {e}")
        raise
