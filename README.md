# SuperMoment

Aplikacija za prikupljanje i šerovanje fotografija i video snimaka iz različitih uglova istog momenta.

## 🎯 O projektu

SuperMoment omogućava korisnicima da prikupe slike i video snimke iz različitih uglova istog događaja. Aplikacija automatski grupuje medijske fajlove prema vremenu i lokaciji, stvarajući jedinstvene "momente" koji se mogu pregledati iz različitih perspektiva.

### Ključne funkcionalnosti

- **Vaučer sistem** - Admin može kreirati vaučere za događaje i pozvati učesnike
- **Precizno vremensko grupisanje** - Automatsko grupovanje snimaka po sekundi/milisekundi
- **Geolokacija** - Grupovanje događaja po lokaciji
- **Automatski upload** - iOS aplikacija automatski upload-uje medijske fajlove
- **3D vizualizacija** - Pregled pozicija kamera u 3D prostoru
- **Download sistem** - Preuzimanje medija nakon završetka događaja

## 🏗️ Arhitektura

- **Backend**: FastAPI + Python 3.13
- **Frontend**: React + TypeScript + Three.js
- **iOS App**: SwiftUI (u razvoju)
- **Storage**: Lokalno čuvanje fajlova (MVP)
- **Database**: In-memory storage (MVP)

## 📁 Struktura projekta

```
SuperMoment/
├── backend/                 # FastAPI backend
│   ├── main.py             # Glavna aplikacija
│   ├── requirements.txt    # Python dependencies
│   └── uploads/           # Direktorijum za fajlove
├── frontend/               # React admin panel
│   ├── src/
│   │   ├── components/    # React komponente
│   │   ├── pages/         # Stranice aplikacije
│   │   └── services/      # API servisi
│   └── package.json       # Node.js dependencies
├── ios-app/               # iOS SwiftUI aplikacija
├── docs/                  # Dokumentacija
├── docker/                # Docker konfiguracija
├── scripts/               # Setup i start skripte
└── README.md              # Ova datoteka
```

## 🚀 Brzi start

### 1. Kloniranje repozitorijuma

```bash
git clone https://github.com/sgazz/SuperMoment.git
cd SuperMoment
```

### 2. Automatski setup

```bash
./scripts/setup.sh
```

### 3. Pokretanje aplikacije

#### Opcija 1: Korišćenje .command fajlova (macOS)
```bash
# Univerzalni launcher sa meni sistemom
./SuperMoment.command
```

#### Opcija 2: Korišćenje skripti
```bash
./scripts/start.sh
```

Aplikacija će biti dostupna na:
- **Backend API**: http://localhost:8000
- **Frontend Admin**: http://localhost:3000
- **API Dokumentacija**: http://localhost:8000/docs

## 🔧 Ručni setup

### Backend Setup

```bash
# Kreiranje virtualnog okruženja
python3 -m venv supermoment-env

# Aktivacija (macOS/Linux)
source supermoment-env/bin/activate

# Aktivacija (Windows)
supermoment-env\Scripts\activate

# Instalacija dependencies
cd backend
pip install -r requirements.txt

# Pokretanje servera
python main.py
```

### Frontend Setup

```bash
cd frontend

# Instalacija dependencies
npm install

# Pokretanje development servera
npm start
```

## 📱 Korišćenje aplikacije

### 1. Kreiranje događaja

1. Idite na **Događaji** stranicu
2. Kliknite **"Kreiraj novi događaj"**
3. Popunite informacije o događaju
4. Sačuvajte događaj

### 2. Kreiranje vaučera

1. Idite na **Vaučeri** stranicu
2. Kliknite **"Kreiraj novi vaučer"**
3. Izaberite događaj i maksimalan broj učesnika
4. Kopirajte link i pošaljite učesnicima

### 3. Pregled događaja

1. Idite na **Događaji** stranicu
2. Kliknite **"Pregledaj"** na željenom događaju
3. Koristite 3D vizualizaciju za pregled pozicija kamera
4. Pregledajte sve momente u desnoj koloni

## 🔌 API Endpoints

### Događaji

- `POST /events/create` - Kreiranje novog događaja
- `GET /events/{event_id}` - Dohvatanje informacija o događaju
- `POST /events/{event_id}/upload` - Upload medijskog fajla
- `GET /events/{event_id}/moments` - Dohvatanje momenata

### Vaučeri

- `POST /vouchers/create` - Kreiranje novog vaučera
- `POST /vouchers/{voucher_id}/join` - Pridruživanje vaučeru

## 🛠️ Razvoj

### Brzo pokretanje (macOS)
```bash
# Univerzalni launcher sa meni sistemom
./SuperMoment.command
```

### Individualno pokretanje

#### Backend Development
```bash
cd backend
source ../supermoment-env/bin/activate
uvicorn main:app --reload --port 8000
```

#### Frontend Development
```bash
cd frontend
npm start
```

### Dodavanje novih funkcionalnosti

1. **Backend**: Dodajte nove endpoint-e u `backend/main.py`
2. **Frontend**: Kreirajte nove komponente u `frontend/src/`
3. **iOS**: Implementirajte funkcionalnost u iOS aplikaciji

## 🧪 Testiranje

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 📦 Deployment

### Backend Deployment

```bash
cd backend
pip install -r requirements.txt
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend Deployment

```bash
cd frontend
npm run build
# Deploy build/ folder na web server
```

## 🤝 Doprinosi

1. Fork repozitorijuma
2. Kreirajte feature branch (`git checkout -b feature/amazing-feature`)
3. Commit promene (`git commit -m 'Add amazing feature'`)
4. Push na branch (`git push origin feature/amazing-feature`)
5. Otvorite Pull Request

## 📄 Licenca

Ovaj projekat je pod MIT licencom. Pogledajte `LICENSE` fajl za detalje.

## 📞 Kontakt

- **GitHub**: [@sgazz](https://github.com/sgazz)
- **Projekat**: [SuperMoment](https://github.com/sgazz/SuperMoment)

## 🔮 Budući planovi

- [ ] Integracija sa Supabase
- [ ] Real-time notifikacije
- [ ] Napredna 3D vizualizacija
- [ ] iOS aplikacija
- [ ] Android aplikacija
- [ ] AI analiza medija
- [ ] Cloud storage integracija
