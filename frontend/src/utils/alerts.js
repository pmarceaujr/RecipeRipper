// helpers/alerts.js
export const showAlert = async ({
  title = 'Notice',
  text = '',
  html = '',
  icon = 'info',
  confirmButtonText = 'OK',
  showCancelButton = false,
  cancelButtonText = 'Cancel',
  onConfirm = () => {},
  onCancel = () => {},
  timer = null,
  allowOutsideClick = true,
} = {}) => {
  const result = await Swal.fire({
    title,
    text,
    html,
    icon,
    confirmButtonText,
    showCancelButton,
    cancelButtonText,
    timer,
    allowOutsideClick,
    reverseButtons: showCancelButton,
  });

  if (result.isConfirmed) {
    onConfirm();
  } else if (result.dismiss === Swal.DismissReason.cancel) {
    onCancel();
  }

  return result;
};