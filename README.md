# 🚗 TelavendeLele — Non solo Auto

> Il primo salone virtuale sul Lago di Como. Una piattaforma che collega il mercato automobilistico tedesco con clienti italiani della regione del Lago di Como.

**Live:** [intelligentresponder-max.github.io/telavendelele](https://intelligentresponder-max.github.io/telavendelele/)
**Dominio:** [www.telavendelele.it](https://www.telavendelele.it)

---

## Cos'è

TelavendeLele mette in contatto chi vende auto in Germania con acquirenti italiani al Lago di Como. Ogni veicolo viene presentato con un video reale (60 secondi, pregi e difetti), controllato sul posto dal partner tedesco, e consegnato al cliente con bonifico immediato e trasferimento.

La rete si basa su tre ruoli:

- **Lele (Gabriele Agliati)** — il volto italiano, gestisce i clienti al Lago di Como
- **Nasir Automobile** — partner e rappresentante in loco nella regione Francoforte/Rhein-Main
- **ASGlobal (André Schwarz)** — piattaforma digitale, acquisizione venditori e tecnologia

---

## Pagine del sito

| Pagina | File | Descrizione |
|--------|------|-------------|
| Salone principale | `index.html` | Vetrina veicoli, bilingue IT/DE |
| Vendi (IT) | `vendi.html` | Pagina per venditori italiani — invio video auto |
| Verkaufen (DE) | `verkaufen.html` | Versione tedesca della pagina di vendita |
| Canale video | `canale.html` | Galleria dei video dei veicoli |
| Autisti | `autisti.html` | Registrazione autisti di trasferimento (patente italiana) |
| Partner | `partner.html` | Pagina di Nasir Automobile |
| ASGlobal | `asglobal.html` | Il partner digitale e di acquisizione |
| Agente ricerca | `fahrzeug-agent.html` | Strumento di ricerca veicoli |

### Strumenti interni (non indicizzati)

| Strumento | File | Uso |
|-----------|------|-----|
| Deal-Magie 777 | `deal-magie.html` | Calcolatore di margine e ripartizione utili |

---

## Materiali di marketing

- `whatsapp-katalog.png` — immagine catalogo WhatsApp Business (IT)
- `whatsapp-katalog-de.png` — immagine catalogo WhatsApp Business (DE)
- `qr-poster-vendi.png` — poster QR stampabile per il Lago di Como
- `qr-vendi.png` — QR code semplice verso la pagina di vendita
- `onepager-kooperation.pdf` — concetto di cooperazione (3 pagine: Lele / ASGlobal / Nasir)

---

## Design

Sistema visivo coerente su tutte le pagine:

- **Colori:** oro `#B8963E`, nero `#0D0D0D`, crema `#F5EDD8`
- **Font:** Cormorant Garamond (titoli) + Montserrat (testo)
- **Stile:** elegante, sfondo scuro con accenti dorati

---

## SEO

- `sitemap.xml` — mappa del sito per i motori di ricerca
- `robots.txt` — istruzioni per i crawler
- Meta tag Open Graph e Twitter Card su `index.html`
- Dati strutturati Schema.org (`AutoDealer`)
- `hreflang` per le versioni IT/DE

---

## Contatti

- **WhatsApp:** +39 366 117 8347
- **Instagram:** [@telavendelelenonsoloauto](https://www.instagram.com/telavendelelenonsoloauto)
- **Facebook:** [Telavendelele Non solo Auto](https://www.facebook.com/Telavendelelelenonsoloauto)
- **Email:** telavendelele@gmail.com

---

## Note tecniche

Sito statico ospitato su GitHub Pages. Nessun backend — i form inviano i dati direttamente via WhatsApp (conforme GDPR, nessun salvataggio sul sito). Deploy automatico tramite GitHub Actions (`.github/workflows/deploy.yml`).

---

*© 2026 TelavendeLele · Gabriele Agliati — Lago di Como · Piattaforma a cura di ASGlobal*
