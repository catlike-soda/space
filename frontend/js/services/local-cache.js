/** IndexedDB local cache for offline dictionary. */
const LocalCache = {
  _db: null,

  async _open() {
    if (this._db) return this._db;
    return new Promise((resolve, reject) => {
      const req = indexedDB.open("korean-app", 1);
      req.onupgradeneeded = (e) => {
        const db = e.target.result;
        if (!db.objectStoreNames.contains("dictionary")) {
          db.createObjectStore("dictionary", { keyPath: "id" });
        }
        if (!db.objectStoreNames.contains("favorites")) {
          db.createObjectStore("favorites", { keyPath: "word_id" });
        }
        if (!db.objectStoreNames.contains("settings")) {
          db.createObjectStore("settings", { keyPath: "key" });
        }
      };
      req.onsuccess = (e) => {
        this._db = e.target.result;
        resolve(this._db);
      };
      req.onerror = () => reject(req.error);
    });
  },

  async put(storeName, data) {
    const db = await this._open();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, "readwrite");
      const store = tx.objectStore(storeName);
      store.put(data);
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  },

  async getAll(storeName) {
    const db = await this._open();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, "readonly");
      const store = tx.objectStore(storeName);
      const req = store.getAll();
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  },

  async get(storeName, key) {
    const db = await this._open();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, "readonly");
      const store = tx.objectStore(storeName);
      const req = store.get(key);
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  },

  async remove(storeName, key) {
    const db = await this._open();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, "readwrite");
      const store = tx.objectStore(storeName);
      store.delete(key);
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  },

  async isFavorite(wordId) {
    const fav = await this.get("favorites", wordId);
    return !!fav;
  },

  async toggleFavorite(word) {
    const exists = await this.isFavorite(word.id);
    if (exists) {
      await this.remove("favorites", word.id);
      await API.removeFavorite(word.id);
      return false;
    } else {
      await this.put("favorites", { word_id: word.id, word });
      await API.addFavorite(word.id);
      return true;
    }
  },

  async getSettings() {
    const dark = await this.get("settings", "darkMode");
    const accent = await this.get("settings", "accentColor");
    return {
      darkMode: dark ? dark.value : true,
      accentColor: accent ? accent.value : "#2DD4BF",
    };
  },

  async saveSetting(key, value) {
    await this.put("settings", { key, value });
  },
};
