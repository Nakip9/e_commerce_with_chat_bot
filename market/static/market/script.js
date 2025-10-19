(function () {
  const STORAGE_KEY = "autodrive-preferred-language";

  function setLanguage(lang) {
    const isArabic = lang === "ar";
    const html = document.documentElement;
    const body = document.body;

    document.querySelectorAll("[data-lang-en]").forEach((node) => {
      const english = node.dataset.langEn;
      const arabic = node.dataset.langAr;
      const text = isArabic ? arabic : english;
      if (typeof text === "undefined") {
        return;
      }

      const tag = node.tagName.toLowerCase();
      if (tag === "input" || tag === "textarea") {
        return;
      }

      if (tag === "option") {
        node.textContent = text;
        return;
      }

      if (tag === "title") {
        document.title = text;
      }

      node.textContent = text;
    });

    document.querySelectorAll("[data-placeholder-en]").forEach((node) => {
      const english = node.dataset.placeholderEn;
      const arabic = node.dataset.placeholderAr;
      const text = isArabic ? arabic : english;
      if (typeof text !== "undefined") {
        node.placeholder = text;
      }
    });

    document.querySelectorAll("[data-dir-toggle]").forEach((node) => {
      node.dir = isArabic ? "rtl" : "ltr";
    });

    html.lang = isArabic ? "ar" : "en";
    html.dir = isArabic ? "rtl" : "ltr";
    body.setAttribute("dir", isArabic ? "rtl" : "ltr");

    document.querySelectorAll(".lang-switch").forEach((button) => {
      button.classList.toggle("active", button.dataset.lang === lang);
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    const savedLanguage = localStorage.getItem(STORAGE_KEY) || "en";
    setLanguage(savedLanguage);

    document.querySelectorAll(".lang-switch").forEach((button) => {
      button.addEventListener("click", () => {
        const lang = button.dataset.lang || "en";
        localStorage.setItem(STORAGE_KEY, lang);
        setLanguage(lang);
      });
    });
  });
})();
