document.addEventListener("DOMContentLoaded", () => {
  const dialog = document.querySelector("#credential-viewer");
  const openers = [...document.querySelectorAll("[data-credential-open]")];
  if (!dialog || !openers.length || typeof dialog.showModal !== "function") return;

  const image = dialog.querySelector("[data-credential-image]");
  const stage = dialog.querySelector("[data-credential-stage]");
  const zoom = dialog.querySelector("[data-credential-zoom]");
  const close = dialog.querySelector("[data-credential-close]");
  const mode = dialog.querySelector("#credential-viewer-mode");
  let opener = null;
  let native = false;

  const ensureFullImage = () => {
    if (!image || image.hasAttribute("src")) return;
    const src = image.dataset.src;
    if (src) image.setAttribute("src", src);
  };

  const setMode = (value) => {
    native = Boolean(value);
    dialog.classList.toggle("is-native", native);
    if (zoom) {
      zoom.textContent = native ? "Prispôsobiť" : "100 %";
      zoom.setAttribute("aria-pressed", String(native));
      zoom.setAttribute("aria-label", native ? "Prispôsobiť osvedčenie displeju" : "Zobraziť osvedčenie v 100 % natívnej veľkosti");
    }
    if (mode) mode.textContent = native ? "100 % · natívna veľkosť" : "Prispôsobené displeju";
    if (!native && stage) {
      stage.scrollTop = 0;
      stage.scrollLeft = 0;
    }
  };

  const open = (event) => {
    event?.preventDefault();
    opener = event?.currentTarget || null;
    setMode(false);
    dialog.showModal();
    requestAnimationFrame(() => {
      if (!dialog.open) return;
      ensureFullImage();
    });
    close?.focus();
  };

  openers.forEach((button) => button.addEventListener("click", open));
  image?.addEventListener("click", () => {
    if (dialog.open) setMode(!native);
  });
  zoom?.addEventListener("click", () => {
    if (dialog.open) setMode(!native);
  });
  close?.addEventListener("click", () => {
    if (dialog.open) dialog.close();
  });
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });
  dialog.addEventListener("close", () => {
    setMode(false);
    opener?.focus();
    opener = null;
  });
});
