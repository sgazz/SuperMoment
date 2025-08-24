# 🚀 SuperMoment - Brzo pokretanje

## macOS - Najlakši način

### 1. Dvoklik na .command fajl
```bash
# Univerzalni launcher sa meni sistemom
SuperMoment.command
```

### 2. Ili iz terminala
```bash
./SuperMoment.command
```

## Šta se dešava kada pokrenete .command fajl:

### SuperMoment Universal Launcher
Otvara se meni sa sledećim opcijama:

1️⃣ **🚀 Pokreni servise** - Pokreće backend i frontend
2️⃣ **🌐 Pokreni + otvori browser** - Pokreće servise i otvara browser
3️⃣ **🔍 Proveri status** - Proverava da li servisi rade
4️⃣ **🛑 Zaustavi servise** - Zaustavlja sve SuperMoment procese
5️⃣ **🔄 Restart servisa** - Restartuje sve servise
6️⃣ **📚 Otvori API dokumentaciju** - Otvara Swagger UI
7️⃣ **🎨 Otvori frontend admin** - Otvara React aplikaciju
8️⃣ **🔧 Otvori backend API** - Otvara backend root
9️⃣ **❌ Izlaz** - Zatvara launcher

### Automatske provere:
- ✅ **Proverava virtualno okruženje** - Aktivira Python env ako nije aktivan
- ✅ **Proverava dependencies** - Instalira npm pakete ako nedostaju
- ✅ **Proverava da li su servisi već pokrenuti** - Sprečava duplikate
- ✅ **Proverava status pokretanja** - Osigurava da su servisi pokrenuti

## Dostupni linkovi:

- 🌐 **Frontend**: http://localhost:3000
- 🔧 **Backend API**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/docs

## Zaustavljanje:

Pritisnite **Ctrl+C** u terminalu da zaustavite sve servise.

## Troubleshooting:

### Problem: "Permission denied"
```bash
chmod +x SuperMoment.command
```

### Problem: "Niste u SuperMoment direktorijumu"
Idite u SuperMoment folder i pokušajte ponovo.

### Problem: Portovi su zauzeti
```bash
# Proverite koji procesi koriste portove
lsof -i :3000
lsof -i :8000

# Zaustavite procese ako je potrebno
kill -9 <PID>
```

---

**Napomena**: .command fajlovi rade samo na macOS. Za druge sisteme koristite `./scripts/start.sh`
