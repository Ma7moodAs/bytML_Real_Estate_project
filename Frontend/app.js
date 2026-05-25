const API_BASE_URL = "http://127.0.0.1:8000/api";

const state = {
  filters: {
    listingType: "",
    area: "",
    cityKey: "",
  },
  locale: "en",
  selectedProperty: null,
  listingsPayload: null,
  recommendations: [],
  translatedTextCache: new Map(),
  fieldTranslationCache: new Map(),
  inFlightTranslations: new Map(),
  rerenderScheduled: false,
  theme: localStorage.getItem("theme") || "light",
  map: {
    instance: null,
    layerGroup: null,
    initialized: false,
  },
  recommendationSlider: {
    timer: null,
    step: 1,
    pause: false,
    observer: null,
    shouldAutoStart: false,
  },
};

const elements = {
  listingTypeFilter: document.querySelector("#listingTypeFilter"),
  areaFilter: document.querySelector("#areaFilter"),
  resetFiltersButton: document.querySelector("#resetFiltersButton"),
  listingGrid: document.querySelector("#listingGrid"),
  listingCount: document.querySelector("#listingCount"),
  detailsView: document.querySelector("#detailsView"),
  propertyDetails: document.querySelector("#propertyDetails"),
  recommendationList: document.querySelector("#recommendationList"),
  recommendationSlider: document.querySelector("#recommendationSlider"),
  backToListingsButton: document.querySelector("#backToListingsButton"),
  addListingView: document.querySelector("#addListingView"),
  addListingForm: document.querySelector("#addListingForm"),
  showAddListingButton: document.querySelector("#showAddListingButton"),
  showListingsButton: document.querySelector("#showListingsButton"),
  showMapButton: document.querySelector("#showMapButton"),
  themeToggleButton: document.querySelector("#themeToggleButton"),
  homeButton: document.querySelector("#homeButton"),
  languageSelect: document.querySelector("#languageSelect"),
  cancelAddListingButton: document.querySelector("#cancelAddListingButton"),
  formMessage: document.querySelector("#formMessage"),
  salePriceInput: document.querySelector("#salePriceInput"),
  annualPriceInput: document.querySelector("#annualPriceInput"),
  listingTypeInput: document.querySelector("#listingTypeInput"),
  mapView: document.querySelector("#mapView"),
  mapSearchInput: document.querySelector("#mapSearchInput"),
  mapPropertyList: document.querySelector("#mapPropertyList"),
  mapCanvas: document.querySelector("#mapCanvas"),
};

const translations = {
  en: {
    "app.title": "bytML Real Estate",
    "nav.listings": "Listings",
    "nav.home": "Home",
    "nav.map": "Search by map",
    "nav.language": "Language",
    "nav.addListing": "Add listing",
    "nav.themeLight": "Light mode",
    "nav.themeDark": "Dark mode",
    "hero.eyebrow": "Apartments in Jordan",
    "hero.title": "Find a place that fits the way you live.",
    "hero.subtitle":
      "Browse rental and sale apartments, filter by area, and explore similar homes from bytML's content-based recommendation engine.",
    "filters.kicker": "Search",
    "filters.title": "Filters",
    "filters.listingType": "Listing type",
    "filters.area": "Area",
    "filters.allListings": "All listings",
    "filters.allAreas": "All areas",
    "filters.reset": "Reset filters",
    "inventory.kicker": "Inventory",
    "inventory.title": "Available apartments",
    "map.kicker": "Explore",
    "map.title": "Find properties on Jordan map",
    "map.searchLabel": "Search by area or location",
    "map.searchPlaceholder": "Amman",
    "map.searchMapLabel": "Search map location",
    "map.searchMapPlaceholder": "Search location on map",
    "map.noProperties": "No properties found for this search.",
    "map.rentCount": "Rent",
    "map.saleCount": "Sale",
    "map.viewResults": "View",
    "details.backToListings": "Back to listings",
    "details.similarHomes": "Similar homes",
    "details.recommendations": "Recommendations",
    "details.description": "Description",
    "details.specialities": "Specialities",
    "details.noDescription": "No description available.",
    "details.noSpecialities": "No specialities available.",
    "details.noRecommendations": "No recommendations available yet.",
    "footer.copy": "Smart real estate discovery for Jordan.",
    "footer.rights": "© 2026 bytML. All rights reserved.",
    "add.kicker": "Submit",
    "add.title": "Add a property",
    "add.cancel": "Cancel",
    "add.listingType": "Listing type",
    "add.location": "Location",
    "add.locationPlaceholder": "Area, Amman, Jordan",
    "add.bedrooms": "Bedrooms",
    "add.bathrooms": "Bathrooms",
    "add.areaSqm": "Area sqm",
    "add.salePrice": "Sale price",
    "add.annualRentPrice": "Annual rent price",
    "add.floor": "Floor",
    "add.floorPlaceholder": "First floor",
    "add.floorType": "Floor type",
    "add.floorTypePlaceholder": "Normal",
    "add.furnished": "Furnished",
    "add.pool": "Pool",
    "add.description": "Description",
    "add.specialities": "Specialities",
    "add.submit": "Submit listing",
    "common.rent": "Rent",
    "common.sale": "Sale",
    "common.no": "No",
    "common.yes": "Yes",
    "common.furnished": "Furnished",
    "common.unfurnished": "Unfurnished",
    "common.apartmentForRent": "Apartment for rent",
    "common.apartmentForSale": "Apartment for sale",
    "common.in": "in",
    "common.beds": "beds",
    "common.baths": "baths",
    "common.bedrooms": "bedrooms",
    "common.bathrooms": "bathrooms",
    "common.sqm": "sqm",
    "common.listingsFound": "apartments found",
    "common.noApartmentsMatch": "No apartments match these filters.",
    "common.currencySale": "JOD",
    "common.currencyRent": "JOD / year",
    "common.unknownArea": "Unknown area",
    "lang.english": "English",
    "lang.arabic": "Arabic",
    "error.backend": "Could not connect to the backend. Start the API at http://127.0.0.1:8000.",
  },
  ar: {
    "app.title": "bytML للعقارات",
    "nav.listings": "العقارات",
    "nav.home": "الرئيسية",
    "nav.map": "البحث بالخريطة",
    "nav.language": "اللغة",
    "nav.addListing": "إضافة عقار",
    "nav.themeLight": "الوضع الفاتح",
    "nav.themeDark": "الوضع الداكن",
    "hero.eyebrow": "شقق في الأردن",
    "hero.title": "ابحث عن منزل يناسب أسلوب حياتك.",
    "hero.subtitle":
      "تصفح شقق الإيجار والبيع، صفِّ حسب المنطقة، واستكشف منازل مشابهة عبر محرك التوصية في bytML.",
    "filters.kicker": "بحث",
    "filters.title": "الفلاتر",
    "filters.listingType": "نوع الإعلان",
    "filters.area": "المنطقة",
    "filters.allListings": "كل الإعلانات",
    "filters.allAreas": "كل المناطق",
    "filters.reset": "إعادة ضبط الفلاتر",
    "inventory.kicker": "المخزون",
    "inventory.title": "الشقق المتاحة",
    "map.kicker": "استكشاف",
    "map.title": "ابحث عن العقارات على خريطة الأردن",
    "map.searchLabel": "ابحث حسب المنطقة أو الموقع",
    "map.searchPlaceholder": "عمّان",
    "map.searchMapLabel": "ابحث عن موقع على الخريطة",
    "map.searchMapPlaceholder": "ابحث عن موقع على الخريطة",
    "map.noProperties": "لا توجد عقارات مطابقة لبحثك.",
    "map.rentCount": "إيجار",
    "map.saleCount": "بيع",
    "map.viewResults": "عرض",
    "details.backToListings": "العودة إلى العقارات",
    "details.similarHomes": "منازل مشابهة",
    "details.recommendations": "التوصيات",
    "details.description": "الوصف",
    "details.specialities": "المميزات",
    "details.noDescription": "لا يوجد وصف متاح.",
    "details.noSpecialities": "لا توجد مميزات متاحة.",
    "details.noRecommendations": "لا توجد توصيات متاحة حالياً.",
    "footer.copy": "اكتشاف عقاري ذكي في الأردن.",
    "footer.rights": "© 2026 bytML. جميع الحقوق محفوظة.",
    "add.kicker": "إرسال",
    "add.title": "إضافة عقار",
    "add.cancel": "إلغاء",
    "add.listingType": "نوع الإعلان",
    "add.location": "الموقع",
    "add.locationPlaceholder": "المنطقة، عمّان، الأردن",
    "add.bedrooms": "غرف النوم",
    "add.bathrooms": "الحمّامات",
    "add.areaSqm": "المساحة م²",
    "add.salePrice": "سعر البيع",
    "add.annualRentPrice": "سعر الإيجار السنوي",
    "add.floor": "الطابق",
    "add.floorPlaceholder": "الطابق الأول",
    "add.floorType": "نوع الطابق",
    "add.floorTypePlaceholder": "عادي",
    "add.furnished": "مفروش",
    "add.pool": "مسبح",
    "add.description": "الوصف",
    "add.specialities": "المميزات",
    "add.submit": "إرسال العقار",
    "common.rent": "إيجار",
    "common.sale": "بيع",
    "common.no": "لا",
    "common.yes": "نعم",
    "common.furnished": "مفروش",
    "common.unfurnished": "غير مفروش",
    "common.apartmentForRent": "شقة للإيجار",
    "common.apartmentForSale": "شقة للبيع",
    "common.in": "في",
    "common.beds": "غرف",
    "common.baths": "حمّامات",
    "common.bedrooms": "غرف نوم",
    "common.bathrooms": "حمّامات",
    "common.sqm": "م²",
    "common.listingsFound": "شقة متاحة",
    "common.noApartmentsMatch": "لا توجد شقق مطابقة لهذه الفلاتر.",
    "common.currencySale": "د.أ",
    "common.currencyRent": "د.أ / سنوي",
    "common.unknownArea": "منطقة غير معروفة",
    "lang.english": "English",
    "lang.arabic": "العربية",
    "error.backend": "تعذر الاتصال بالخادم. شغّل الـ API على http://127.0.0.1:8000.",
  },
};

const propertyPhotos = [
  "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=1200&q=80",
  "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&w=1200&q=80",
  "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?auto=format&fit=crop&w=1200&q=80",
  "https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=1200&q=80",
  "https://images.unsplash.com/photo-1600566753086-00f18fb6b3ea?auto=format&fit=crop&w=1200&q=80",
  "https://images.unsplash.com/photo-1600607688969-a5bfcd646154?auto=format&fit=crop&w=1200&q=80",
  "https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?auto=format&fit=crop&w=1200&q=80",
  "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=1200&q=80",
];

function t(key) {
  return translations[state.locale][key] ?? translations.en[key] ?? key;
}

function formatPrice(property) {
  const price = Number(property.Final_price ?? property.Sale_price ?? property.Price_annualy ?? 0);
  const suffix = property.Listing_type === "rent" ? ` ${t("common.currencyRent")}` : ` ${t("common.currencySale")}`;
  return `${price.toLocaleString()}${suffix}`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function hasArabicText(value) {
  return /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]/.test(String(value ?? ""));
}

function textDirectionAttrs(value) {
  return hasArabicText(value) ? 'lang="ar" dir="rtl"' : 'lang="en" dir="ltr"';
}

function localizedText(value) {
  return `<span ${textDirectionAttrs(value)}>${escapeHtml(value)}</span>`;
}

function translationKey(property, field) {
  return `${property.apartment_id}:${field}`;
}

function getLocalizedField(property, field) {
  if (state.locale !== "en") return property[field];
  const translated = state.fieldTranslationCache.get(translationKey(property, field));
  return translated ?? property[field];
}

function scheduleLocalizedRerender() {
  if (state.rerenderScheduled) return;
  state.rerenderScheduled = true;
  setTimeout(() => {
    state.rerenderScheduled = false;
    if (state.locale === "en") rerenderLocalizedUI();
  }, 0);
}

async function translateToEnglish(text) {
  const value = String(text ?? "").trim();
  if (!value || !hasArabicText(value)) return value;

  if (state.translatedTextCache.has(value)) {
    return state.translatedTextCache.get(value);
  }

  if (state.inFlightTranslations.has(value)) {
    return state.inFlightTranslations.get(value);
  }

  const translationPromise = (async () => {
    try {
      const url =
        `https://translate.googleapis.com/translate_a/single?client=gtx&sl=ar&tl=en&dt=t&q=${encodeURIComponent(value)}`;
      const response = await fetch(url);
      const payload = await response.json();
      const translated = Array.isArray(payload?.[0])
        ? payload[0].map((part) => part?.[0] || "").join("").trim()
        : "";
      const finalValue = translated || value;
      state.translatedTextCache.set(value, finalValue);
      return finalValue;
    } catch {
      return value;
    } finally {
      state.inFlightTranslations.delete(value);
    }
  })();

  state.inFlightTranslations.set(value, translationPromise);
  return translationPromise;
}

function queuePropertyFieldTranslations(property) {
  if (state.locale !== "en") return;

  const fields = ["Area", "Location", "Floor", "Floor_type", "Description", "Specialities"];
  fields.forEach((field) => {
    const value = property[field];
    if (!value || !hasArabicText(value)) return;

    const cacheKey = translationKey(property, field);
    if (state.fieldTranslationCache.has(cacheKey)) return;

    void translateToEnglish(value).then((translated) => {
      if (translated && translated !== value) {
        state.fieldTranslationCache.set(cacheKey, translated);
        scheduleLocalizedRerender();
      } else {
        state.fieldTranslationCache.set(cacheKey, value);
      }
    });
  });
}

function areaFromLocation(property) {
  const area = getLocalizedField(property, "Area");
  const location = getLocalizedField(property, "Location");
  return area || String(location || "").split(",")[0] || t("common.unknownArea");
}

function listingTypeTitle(property) {
  return property.Listing_type === "rent" ? t("common.apartmentForRent") : t("common.apartmentForSale");
}

function propertyTitleMarkup(property) {
  return `${listingTypeTitle(property)} ${t("common.in")} ${localizedText(areaFromLocation(property))}`;
}

function listingTypeLabel(type) {
  if (type === "rent") return t("common.rent");
  if (type === "sale") return t("common.sale");
  return type;
}

function photoForProperty(property) {
  const id = Number(property.apartment_id ?? 0);
  return propertyPhotos[Math.abs(id) % propertyPhotos.length];
}

function photoBackground(property) {
  return `linear-gradient(180deg, rgba(24, 33, 29, 0.08), rgba(24, 33, 29, 0.42)), url("${photoForProperty(property)}")`;
}

function applyStaticTranslations() {
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    const key = node.getAttribute("data-i18n");
    node.textContent = t(key);
  });

  document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => {
    const key = node.getAttribute("data-i18n-placeholder");
    node.setAttribute("placeholder", t(key));
  });

  document.documentElement.lang = state.locale;
  document.documentElement.dir = state.locale === "ar" ? "rtl" : "ltr";
  document.title = t("app.title");
  elements.languageSelect.value = state.locale;
  updateThemeButtonText();
}

function updateThemeButtonText() {
  elements.themeToggleButton.textContent = state.theme === "dark" ? t("nav.themeLight") : t("nav.themeDark");
}

function applyTheme(theme) {
  state.theme = theme === "dark" ? "dark" : "light";
  document.documentElement.setAttribute("data-theme", state.theme);
  localStorage.setItem("theme", state.theme);
  updateThemeButtonText();
}

function setLanguage(locale) {
  state.locale = locale;
  if (locale === "en") {
    state.fieldTranslationCache.clear();
    state.translatedTextCache.clear();
    state.inFlightTranslations.clear();
  }
  applyStaticTranslations();
  rerenderLocalizedUI();
}

function rerenderLocalizedUI() {
  renderFilterDefaults();
  if (state.listingsPayload) renderListings(state.listingsPayload);
  if (state.selectedProperty) renderDetails(state.selectedProperty);
  renderRecommendations(state.recommendations);
  if (!elements.mapView.classList.contains("hidden")) {
    renderMapPropertyList(state.listingsPayload?.items || [], elements.mapSearchInput.value || "");
  }
}

function renderFilterDefaults() {
  const listingDefault = elements.listingTypeFilter.querySelector('option[value=""]');
  const areaDefault = elements.areaFilter.querySelector('option[value=""]');
  if (listingDefault) listingDefault.textContent = t("filters.allListings");
  if (areaDefault) areaDefault.textContent = t("filters.allAreas");
}

async function fetchJson(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  const payload = await response.json().catch(() => ({}));

  if (!response.ok) {
    const message = payload.detail?.errors?.join(" ") || payload.detail || "Request failed.";
    throw new Error(message);
  }

  return payload;
}

function showView(view) {
  const workspace = document.querySelector("#listings");
  workspace.classList.toggle("hidden", view !== "listings");
  elements.detailsView.classList.toggle("hidden", view !== "details");
  elements.mapView.classList.toggle("hidden", view !== "map");
  elements.addListingView.classList.toggle("hidden", view !== "add");
  if (view !== "details") {
    stopRecommendationAutoscroll();
  } else if (state.recommendationSlider.shouldAutoStart) {
    setupRecommendationVisibilityObserver();
  }
}

function normalizeAreaLabel(value) {
  return String(value ?? "")
    .trim()
    .toLowerCase()
    .replace(/\s+/g, " ");
}

const jordanCityMeta = {
  amman: { labelEn: "Amman", labelAr: "عمّان", coords: [31.9539, 35.9106] },
  irbid: { labelEn: "Irbid", labelAr: "إربد", coords: [32.5569, 35.8479] },
  zarqa: { labelEn: "Zarqa", labelAr: "الزرقاء", coords: [32.0728, 36.088] },
  aqaba: { labelEn: "Aqaba", labelAr: "العقبة", coords: [29.5319, 35.0061] },
  salt: { labelEn: "Salt", labelAr: "السلط", coords: [32.0392, 35.7272] },
  madaba: { labelEn: "Madaba", labelAr: "مادبا", coords: [31.7186, 35.7939] },
  karak: { labelEn: "Karak", labelAr: "الكرك", coords: [31.1854, 35.7048] },
  tafileh: { labelEn: "Tafileh", labelAr: "الطفيلة", coords: [30.8375, 35.6044] },
  maan: { labelEn: "Ma'an", labelAr: "معان", coords: [30.1925, 35.7341] },
  jerash: { labelEn: "Jerash", labelAr: "جرش", coords: [32.2808, 35.8993] },
  ajloun: { labelEn: "Ajloun", labelAr: "عجلون", coords: [32.3326, 35.7517] },
  mafraq: { labelEn: "Mafraq", labelAr: "المفرق", coords: [32.3429, 36.208] },
};

const cityAliases = {
  amman: "amman",
  عمان: "amman",
  ammanjordan: "amman",
  irbid: "irbid",
  اربد: "irbid",
  إربد: "irbid",
  zarqa: "zarqa",
  الزرقاء: "zarqa",
  aqaba: "aqaba",
  العقبة: "aqaba",
  salt: "salt",
  السلط: "salt",
  madaba: "madaba",
  مادبا: "madaba",
  karak: "karak",
  الكرك: "karak",
  tafileh: "tafileh",
  الطفيلة: "tafileh",
  maan: "maan",
  "ma'an": "maan",
  معان: "maan",
  jerash: "jerash",
  جرش: "jerash",
  ajloun: "ajloun",
  عجلون: "ajloun",
  mafraq: "mafraq",
  المفرق: "mafraq",
};

function parseCityKey(property) {
  const area = String(property.Area || "").trim();
  const location = String(property.Location || "").trim();
  const source = `${area},${location}`.toLowerCase();
  const sourceNoSpace = source.replace(/\s+/g, "");

  for (const [alias, cityKey] of Object.entries(cityAliases)) {
    const aliasNorm = alias.toLowerCase();
    if (source.includes(aliasNorm) || sourceNoSpace.includes(aliasNorm.replace(/\s+/g, ""))) {
      return cityKey;
    }
  }

  return "amman";
}

function cityLabel(cityKey) {
  const meta = jordanCityMeta[cityKey] || jordanCityMeta.amman;
  return state.locale === "ar" ? meta.labelAr : meta.labelEn;
}

function areaLabelFromProperty(property) {
  const area = String(property.Area || "").trim();
  if (area) return area;
  return String(property.Location || "").split(",")[0].trim() || t("common.unknownArea");
}

function areaCoords(areaLabel, cityKey) {
  const base = (jordanCityMeta[cityKey] || jordanCityMeta.amman).coords;
  const seed = normalizeAreaLabel(areaLabel);
  let hash = 0;
  for (let i = 0; i < seed.length; i += 1) hash = (hash << 5) - hash + seed.charCodeAt(i);
  const latOffset = ((Math.abs(hash) % 120) / 1000) - 0.06;
  const lngOffset = ((Math.abs(hash >> 8) % 140) / 1000) - 0.07;
  return [base[0] + latOffset, base[1] + lngOffset];
}

function getLocationStats(items, searchTerm = "") {
  const normalized = searchTerm.trim().toLowerCase();
  const grouped = new Map();

  items.forEach((property) => {
    const cityKey = parseCityKey(property);
    const areaName = areaLabelFromProperty(property);
    const areaText = String(areaName || "").toLowerCase();
    const locationText = String(getLocalizedField(property, "Location") || "").toLowerCase();
    if (normalized && !areaText.includes(normalized) && !locationText.includes(normalized)) return;

    const key = normalizeAreaLabel(areaName);
    if (!grouped.has(key)) {
      grouped.set(key, {
        area: areaName,
        rent: 0,
        sale: 0,
        total: 0,
        coords: areaCoords(areaName, cityKey),
      });
    }

    const row = grouped.get(key);
    row.area = areaName;
    row.total += 1;
    if (property.Listing_type === "rent") row.rent += 1;
    if (property.Listing_type === "sale") row.sale += 1;
  });

  return Array.from(grouped.values()).sort((a, b) => b.total - a.total);
}

function applyLocationTypeFilter(area, listingType) {
  state.filters.cityKey = "";
  state.filters.area = "";
  state.filters.listingType = listingType;
  const matchingAreaOption = Array.from(elements.areaFilter.options).find((option) => option.value === area);
  if (matchingAreaOption) {
    state.filters.area = area;
    elements.areaFilter.value = area;
  } else {
    elements.areaFilter.value = "";
  }
  elements.listingTypeFilter.value = listingType;
  showView("listings");
  window.scrollTo({ top: 0, behavior: "smooth" });
  void loadListings();
}

function popupContentForLocation(stat) {
  return `
    <div class="map-popup">
      <strong>${escapeHtml(stat.area)}</strong>
      <div class="map-popup-actions">
        <button class="map-popup-action" data-area="${escapeHtml(stat.area)}" data-type="rent" ${stat.rent ? "" : "disabled"}>
          ${t("map.rentCount")}: ${stat.rent} · ${t("map.viewResults")}
        </button>
        <button class="map-popup-action" data-area="${escapeHtml(stat.area)}" data-type="sale" ${stat.sale ? "" : "disabled"}>
          ${t("map.saleCount")}: ${stat.sale} · ${t("map.viewResults")}
        </button>
      </div>
    </div>
  `;
}

function ensureMap() {
  if (state.map.initialized) return;

  state.map.instance = L.map(elements.mapCanvas, {
    center: [31.2, 36.2],
    zoom: 8,
    minZoom: 7,
  });

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(state.map.instance);

  state.map.layerGroup = L.layerGroup().addTo(state.map.instance);
  state.map.initialized = true;
}

function renderMapPins(stats) {
  ensureMap();
  state.map.layerGroup.clearLayers();

  stats.forEach((stat) => {
    const marker = L.marker(stat.coords, { title: stat.area });
    marker.bindPopup(popupContentForLocation(stat), { closeButton: true });
    marker.on("mouseover", () => marker.openPopup());
    marker.on("popupopen", (event) => {
      const container = event.popup.getElement();
      if (!container) return;
      container.querySelectorAll(".map-popup-action").forEach((button) => {
        button.addEventListener("click", () => {
          const area = button.getAttribute("data-area");
          const type = button.getAttribute("data-type");
          if (!area || !type) return;
          applyLocationTypeFilter(area, type);
        });
      });
    });
    marker.on("click", () => {
      renderMapPropertyPreviewByArea(stat.area);
    });
    marker.addTo(state.map.layerGroup);
  });

  if (stats.length) {
    const bounds = L.latLngBounds(stats.map((item) => item.coords));
    state.map.instance.fitBounds(bounds.pad(0.18));
  }
}

function renderMapPropertyList(items, searchTerm = "") {
  const stats = getLocationStats(items, searchTerm);
  const normalized = searchTerm.trim().toLowerCase();
  const matchingProperties = items.filter((property) => {
    const area = String(areaFromLocation(property) || "").toLowerCase();
    const location = String(getLocalizedField(property, "Location") || "").toLowerCase();
    return !normalized || area.includes(normalized) || location.includes(normalized);
  });

  if (!stats.length || !matchingProperties.length) {
    renderMapPropertyCards([]);
    renderMapPins([]);
    return;
  }

  renderMapPins(stats);
  renderMapPropertyCards(matchingProperties);
}

function renderMapPropertyCards(items) {
  elements.mapPropertyList.innerHTML = "";

  if (!items.length) {
    elements.mapPropertyList.innerHTML = `<div class="empty-state">${t("map.noProperties")}</div>`;
    return;
  }

  items.forEach((property) => {
    queuePropertyFieldTranslations(property);
    const localizedArea = areaFromLocation(property);
    const card = document.createElement("button");
    card.type = "button";
    card.className = "map-property-card map-property-card-detailed";
    card.innerHTML = `
      <div class="map-property-image" style='background-image: ${photoBackground(property)}' aria-hidden="true"></div>
      <div class="map-property-body">
        <div class="tag-row">
          <span class="tag">${escapeHtml(listingTypeLabel(property.Listing_type))}</span>
          <span class="tag">${localizedText(localizedArea)}</span>
        </div>
        <div class="map-property-price-line">${formatPrice(property)}</div>
        <strong class="map-property-title">${propertyTitleMarkup(property)}</strong>
        <div class="map-property-location">${localizedText(getLocalizedField(property, "Location") || areaFromLocation(property))}</div>
        <div class="stats-row">
          <span class="stat">${property.Bedrooms} ${t("common.beds")}</span>
          <span class="stat">${property.Bathrooms} ${t("common.baths")}</span>
          <span class="stat">${property.Area_sqm} ${t("common.sqm")}</span>
        </div>
      </div>
    `;
    card.addEventListener("click", () => loadPropertyDetails(property.apartment_id));
    elements.mapPropertyList.appendChild(card);
  });
}

function renderMapPropertyPreviewByArea(areaLabel) {
  const items = state.listingsPayload?.items || [];
  const matched = items.filter(
    (property) => normalizeAreaLabel(areaLabelFromProperty(property)) === normalizeAreaLabel(areaLabel)
  );
  renderMapPropertyCards(matched);
}

function openMapView() {
  showView("map");
  ensureMap();
  setTimeout(() => state.map.instance.invalidateSize(), 0);
  renderMapPropertyList(state.listingsPayload?.items || [], elements.mapSearchInput.value || "");
}

function renderListingCard(property) {
  queuePropertyFieldTranslations(property);
  const card = document.createElement("button");
  card.className = "property-card";
  card.type = "button";
  card.innerHTML = `
    <div class="card-image" style='background-image: ${photoBackground(property)}' aria-hidden="true"></div>
    <div class="card-body">
      <div class="tag-row">
        <span class="tag">${escapeHtml(listingTypeLabel(property.Listing_type))}</span>
        <span class="tag">${localizedText(areaFromLocation(property))}</span>
      </div>
      <div>
        <div class="price">${formatPrice(property)}</div>
        <strong>${propertyTitleMarkup(property)}</strong>
      </div>
      <div class="stats-row">
        <span class="stat">${property.Bedrooms} ${t("common.beds")}</span>
        <span class="stat">${property.Bathrooms} ${t("common.baths")}</span>
        <span class="stat">${property.Area_sqm} ${t("common.sqm")}</span>
      </div>
    </div>
  `;
  card.addEventListener("click", () => loadPropertyDetails(property.apartment_id));
  return card;
}

function renderListings(payload) {
  state.listingsPayload = payload;
  const sourceItems = Array.isArray(payload.items) ? payload.items : [];
  const visibleItems = state.filters.cityKey
    ? sourceItems.filter((property) => parseCityKey(property) === state.filters.cityKey)
    : sourceItems;

  elements.listingGrid.innerHTML = "";
  elements.listingCount.textContent = `${visibleItems.length} ${t("common.listingsFound")}`;

  if (!visibleItems.length) {
    elements.listingGrid.innerHTML = `<div class="empty-state">${t("common.noApartmentsMatch")}</div>`;
    return;
  }

  visibleItems.forEach((property) => {
    elements.listingGrid.appendChild(renderListingCard(property));
  });
}

async function loadListings() {
  const params = new URLSearchParams();
  params.set("limit", "1000");
  if (state.filters.listingType) params.set("listing_type", state.filters.listingType);
  if (state.filters.area) params.set("area", state.filters.area);

  const payload = await fetchJson(`/properties?${params.toString()}`);
  renderListings(payload);
}

async function loadFilters() {
  const filters = await fetchJson("/filters");
  elements.listingTypeFilter.innerHTML = `<option value="">${t("filters.allListings")}</option>`;
  elements.areaFilter.innerHTML = `<option value="">${t("filters.allAreas")}</option>`;

  filters.listing_types.forEach((type) => {
    const option = document.createElement("option");
    option.value = type;
    option.textContent = listingTypeLabel(type);
    elements.listingTypeFilter.appendChild(option);
  });

  filters.areas.forEach((area) => {
    const option = document.createElement("option");
    option.value = area;
    option.textContent = area;
    elements.areaFilter.appendChild(option);
  });

  if (state.locale === "en") {
    void Promise.all(
      filters.areas.map(async (area) => {
        if (!hasArabicText(area)) return;
        const translated = await translateToEnglish(area);
        const option = Array.from(elements.areaFilter.options).find((item) => item.value === area);
        if (option) option.textContent = translated;
      })
    );
  }
}

function renderDetails(property) {
  queuePropertyFieldTranslations(property);
  const floor = getLocalizedField(property, "Floor");
  const floorType = getLocalizedField(property, "Floor_type");
  const description = getLocalizedField(property, "Description");
  const specialities = getLocalizedField(property, "Specialities");

  elements.propertyDetails.innerHTML = `
    <div class="details-image" style='background-image: ${photoBackground(property)}' aria-hidden="true"></div>
    <div class="tag-row">
      <span class="tag">${escapeHtml(listingTypeLabel(property.Listing_type))}</span>
      <span class="tag">${localizedText(areaFromLocation(property))}</span>
      <span class="tag">${property.Furnished ? t("common.furnished") : t("common.unfurnished")}</span>
    </div>
    <h2>${propertyTitleMarkup(property)}</h2>
    <div class="price">${formatPrice(property)}</div>
    <div class="stats-row">
      <span class="stat">${property.Bedrooms} ${t("common.bedrooms")}</span>
      <span class="stat">${property.Bathrooms} ${t("common.bathrooms")}</span>
      <span class="stat">${property.Area_sqm} ${t("common.sqm")}</span>
      <span class="stat">${localizedText(floor)}</span>
      <span class="stat">${localizedText(floorType)}</span>
    </div>
    <div class="description-block">
      <p class="section-kicker">${t("details.description")}</p>
      <p ${textDirectionAttrs(description)}>${escapeHtml(description || t("details.noDescription"))}</p>
    </div>
    <div class="description-block">
      <p class="section-kicker">${t("details.specialities")}</p>
      <p ${textDirectionAttrs(specialities)}>${escapeHtml(specialities || t("details.noSpecialities"))}</p>
    </div>
  `;
}

function renderRecommendations(items) {
  state.recommendations = items;
  elements.recommendationList.innerHTML = "";
  stopRecommendationAutoscroll();
  state.recommendationSlider.shouldAutoStart = false;

  if (!items.length) {
    elements.recommendationList.innerHTML = `<div class="empty-state">${t("details.noRecommendations")}</div>`;
    return;
  }

  const sourceItems = items.length > 1 ? [...items, ...items] : [...items];

  sourceItems.forEach((property) => {
    queuePropertyFieldTranslations(property);
    const location = getLocalizedField(property, "Location") || areaFromLocation(property);
    const card = document.createElement("button");
    card.className = "recommendation-card";
    card.type = "button";
    card.innerHTML = `
      <div class="recommendation-image recommendation-image-large" style='background-image: ${photoBackground(property)}' aria-hidden="true">
        <span class="recommendation-price-badge">${formatPrice(property)}</span>
        <div class="recommendation-icon-row" aria-hidden="true">
          <span class="recommendation-icon-btn">♡</span>
          <span class="recommendation-icon-btn">⚖</span>
          <span class="recommendation-icon-btn">⤴</span>
        </div>
      </div>
      <div class="recommendation-copy recommendation-copy-large">
        <strong class="recommendation-title">${propertyTitleMarkup(property)}</strong>
        <div class="recommendation-location">${localizedText(location)}</div>
        <div class="recommendation-specs">
          <span>${property.Bedrooms} ${t("common.beds")}</span>
          <span>${property.Bathrooms} ${t("common.baths")}</span>
          <span>${property.Area_sqm} ${t("common.sqm")}</span>
        </div>
        <div class="recommendation-footer">
          <span class="recommendation-type">${property.Listing_type === "rent" ? t("common.rent") : t("common.sale")}</span>
          <span class="recommendation-brand">bytML Real Estate</span>
        </div>
      </div>
    `;
    card.addEventListener("click", () => loadPropertyDetails(property.apartment_id));
    elements.recommendationList.appendChild(card);
  });

  state.recommendationSlider.shouldAutoStart = true;
  setupRecommendationVisibilityObserver();
}

function stopRecommendationAutoscroll() {
  if (state.recommendationSlider.timer) {
    clearInterval(state.recommendationSlider.timer);
    state.recommendationSlider.timer = null;
  }
}

function startRecommendationAutoscroll() {
  const slider = elements.recommendationSlider;
  const list = elements.recommendationList;
  if (!slider || !list || state.recommendations.length <= 1) return;
  if (state.recommendationSlider.timer) return;
  if (!list.scrollWidth) return;

  slider.scrollLeft = 0;
  const resetPoint = list.scrollWidth / 2;
  state.recommendationSlider.timer = setInterval(() => {
    if (!state.recommendationSlider.pause) {
      slider.scrollLeft += state.recommendationSlider.step;
      if (slider.scrollLeft >= resetPoint) {
        slider.scrollLeft = 0;
      }
    }
  }, 16);
}

function setupRecommendationVisibilityObserver() {
  const slider = elements.recommendationSlider;
  if (!slider) return;

  if (state.recommendationSlider.observer) {
    state.recommendationSlider.observer.disconnect();
    state.recommendationSlider.observer = null;
  }

  state.recommendationSlider.observer = new IntersectionObserver(
    (entries) => {
      const entry = entries[0];
      if (!entry || !state.recommendationSlider.shouldAutoStart) return;

      if (entry.isIntersecting) {
        startRecommendationAutoscroll();
      } else {
        stopRecommendationAutoscroll();
      }
    },
    {
      root: null,
      threshold: 0.35,
    }
  );

  state.recommendationSlider.observer.observe(slider);
}

async function loadPropertyDetails(apartmentId) {
  const [property, recommendations] = await Promise.all([
    fetchJson(`/properties/${apartmentId}`),
    fetchJson(`/properties/${apartmentId}/recommendations`),
  ]);

  state.selectedProperty = property;
  renderDetails(property);
  renderRecommendations(recommendations.items);
  showView("details");
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function updatePriceRequirements() {
  const listingType = elements.listingTypeInput.value;
  elements.salePriceInput.required = listingType === "sale";
  elements.annualPriceInput.required = listingType === "rent";
}

function formValue(formData, key) {
  const value = formData.get(key);
  return value === "" ? null : value;
}

async function handleAddListing(event) {
  event.preventDefault();
  elements.formMessage.textContent = "";

  const formData = new FormData(elements.addListingForm);
  const payload = {
    Listing_type: formValue(formData, "Listing_type"),
    Location: formValue(formData, "Location"),
    Bedrooms: Number(formValue(formData, "Bedrooms")),
    Bathrooms: Number(formValue(formData, "Bathrooms")),
    Area_sqm: Number(formValue(formData, "Area_sqm")),
    Sale_price: formValue(formData, "Sale_price") ? Number(formValue(formData, "Sale_price")) : null,
    Price_annualy: formValue(formData, "Price_annualy") ? Number(formValue(formData, "Price_annualy")) : null,
    Price_monthly: null,
    Furnished: formValue(formData, "Furnished") === "true",
    Pool: formValue(formData, "Pool") === "true",
    Floor: formValue(formData, "Floor"),
    Floor_type: formValue(formData, "Floor_type"),
    Description: formValue(formData, "Description"),
    Specialities: formValue(formData, "Specialities"),
    URL: null,
  };

  try {
    const createdProperty = await fetchJson("/properties", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    elements.addListingForm.reset();
    updatePriceRequirements();
    await loadFilters();
    await loadListings();
    await loadPropertyDetails(createdProperty.apartment_id);
  } catch (error) {
    elements.formMessage.textContent = error.message;
  }
}

function bindEvents() {
  elements.listingTypeFilter.addEventListener("change", async (event) => {
    state.filters.listingType = event.target.value;
    await loadListings();
  });

  elements.areaFilter.addEventListener("change", async (event) => {
    state.filters.cityKey = "";
    state.filters.area = event.target.value;
    await loadListings();
  });

  elements.resetFiltersButton.addEventListener("click", async () => {
    state.filters.cityKey = "";
    state.filters.listingType = "";
    state.filters.area = "";
    elements.listingTypeFilter.value = "";
    elements.areaFilter.value = "";
    await loadListings();
  });

  elements.backToListingsButton.addEventListener("click", () => showView("listings"));
  elements.homeButton.addEventListener("click", () => {
    showView("listings");
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
  elements.showMapButton.addEventListener("click", openMapView);
  elements.showListingsButton.addEventListener("click", () => showView("listings"));
  elements.showAddListingButton.addEventListener("click", () => {
    updatePriceRequirements();
    showView("add");
  });
  elements.cancelAddListingButton.addEventListener("click", () => showView("listings"));
  elements.languageSelect.addEventListener("change", (event) => {
    setLanguage(event.target.value === "ar" ? "ar" : "en");
  });
  elements.themeToggleButton.addEventListener("click", () => {
    applyTheme(state.theme === "dark" ? "light" : "dark");
  });
  elements.recommendationSlider.addEventListener("mouseenter", () => {
    state.recommendationSlider.pause = true;
  });
  elements.recommendationSlider.addEventListener("mouseleave", () => {
    state.recommendationSlider.pause = false;
  });
  elements.recommendationSlider.addEventListener("touchstart", () => {
    state.recommendationSlider.pause = true;
  });
  elements.recommendationSlider.addEventListener("touchend", () => {
    state.recommendationSlider.pause = false;
  });
  elements.mapSearchInput.addEventListener("input", (event) => {
    renderMapPropertyList(state.listingsPayload?.items || [], event.target.value || "");
  });
  elements.mapSearchInput.addEventListener("keydown", async (event) => {
    if (event.key !== "Enter") return;
    event.preventDefault();
    const query = event.target.value.trim();
    if (!query) return;

    const localStats = getLocationStats(state.listingsPayload?.items || [], query);
    if (localStats.length) {
      const target = localStats[0];
      ensureMap();
      state.map.instance.flyTo(target.coords, Math.max(state.map.instance.getZoom(), 11));
      renderMapPropertyPreviewByArea(target.area);
      return;
    }

    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(`${query}, Jordan`)}&limit=1`
      );
      const results = await response.json();
      if (results?.length) {
        const lat = Number(results[0].lat);
        const lon = Number(results[0].lon);
        if (!Number.isNaN(lat) && !Number.isNaN(lon)) {
          ensureMap();
          state.map.instance.flyTo([lat, lon], 12);
        }
      }
    } catch {
      // Keep current map state if geocoding fails.
    }
  });
  elements.listingTypeInput.addEventListener("change", updatePriceRequirements);
  elements.addListingForm.addEventListener("submit", handleAddListing);
}

async function init() {
  try {
    applyTheme(state.theme);
    applyStaticTranslations();
    bindEvents();
    updatePriceRequirements();
    await loadFilters();
    await loadListings();
  } catch (error) {
    elements.listingGrid.innerHTML = `
      <div class="empty-state">
        ${t("error.backend")}
      </div>
    `;
  }
}

init();
