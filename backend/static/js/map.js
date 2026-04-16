// ─────────────────────────────────────────
// RaktSetu — Live Donor Map (Leaflet.js)
// ─────────────────────────────────────────

// Initialize map centered on India
const map = L.map("map").setView([19.0760, 72.8777], 11); // Default: Mumbai

// Load OpenStreetMap tiles (completely free)
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: '© <a href="https://openstreetmap.org">OpenStreetMap</a>',
  maxZoom: 18
}).addTo(map);

// Marker layers
let donorLayer    = L.layerGroup().addTo(map);
let myLocLayer    = L.layerGroup().addTo(map);
let userMarker    = null;

// ── CUSTOM MARKER ICONS ──
const redIcon = L.divIcon({
  html: `<div style="
    background:#CC0000; color:white; border-radius:50% 50% 50% 0;
    width:32px; height:32px; display:flex; align-items:center;
    justify-content:center; font-size:14px; font-weight:700;
    transform:rotate(-45deg); box-shadow:0 2px 6px rgba(0,0,0,0.3);
  "><span style="transform:rotate(45deg)">🩸</span></div>`,
  className: "",
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32]
});

const orangeIcon = L.divIcon({
  html: `<div style="
    background:#FF8800; color:white; border-radius:50% 50% 50% 0;
    width:32px; height:32px; display:flex; align-items:center;
    justify-content:center; font-size:14px; font-weight:700;
    transform:rotate(-45deg); box-shadow:0 2px 6px rgba(0,0,0,0.3);
  "><span style="transform:rotate(45deg)">🩸</span></div>`,
  className: "",
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32]
});

const blueIcon = L.divIcon({
  html: `<div style="
    background:#1F4E79; color:white; border-radius:50%;
    width:20px; height:20px; border:3px solid white;
    box-shadow:0 2px 6px rgba(0,0,0,0.4);
  "></div>`,
  className: "",
  iconSize: [20, 20],
  iconAnchor: [10, 10]
});


// ── LOAD ALL ACTIVE DONORS ──
async function loadDonors() {
  donorLayer.clearLayers();

  const bloodGroup = document.getElementById("filterBlood").value;

  try {
    const result = await DonorAPI.getActive(bloodGroup);

    if (!result.success) {
      document.getElementById("donorCount").textContent = "Could not load donors.";
      return;
    }

    const donors = result.data;
    let plotted = 0;

    donors.forEach(donor => {
      // Skip donors without GPS
      if (!donor.latitude || !donor.longitude) return;

      const lat = parseFloat(donor.latitude);
      const lon = parseFloat(donor.longitude);

      // Determine eligibility for icon color
      const lastDonated = donor.last_donated ? new Date(donor.last_donated) : null;
      const daysSince   = lastDonated
        ? Math.floor((Date.now() - lastDonated.getTime()) / (1000 * 60 * 60 * 24))
        : 999;
      const eligible = daysSince >= 90;

      // Build popup content
      const popup = `
        <div class="donor-popup">
          <div class="popup-name">${donor.name}</div>
          <div class="popup-blood">${donor.blood_group}</div>
          <div class="popup-row">📍 ${donor.city || "Location available"}</div>
          <div class="popup-row">
            ${eligible
              ? "✅ Eligible to donate"
              : `⏳ Eligible in ${90 - daysSince} days`}
          </div>
          <div class="popup-row" style="margin-top:6px; font-size:12px; color:#888;">
            Last confirmed: ${
              donor.last_confirmed
                ? new Date(donor.last_confirmed).toLocaleDateString("en-IN")
                : "Unknown"
            }
          </div>
        </div>
      `;

      // Add marker to map
      L.marker([lat, lon], { icon: eligible ? redIcon : orangeIcon })
        .addTo(donorLayer)
        .bindPopup(popup);

      plotted++;
    });

    // Update count banner
    const bloodLabel = bloodGroup ? `(${bloodGroup})` : "";
    document.getElementById("donorCount").textContent =
      `🩸 ${plotted} active verified donors found on map ${bloodLabel}`;

    // If no donors have GPS — show message
    if (plotted > 0) {
      const firstDonor = donors.find(d => d.latitude && d.longitude);
      if (firstDonor) {
        map.setView([parseFloat(firstDonor.latitude), parseFloat(firstDonor.longitude)], 13);
      }
    }

  } catch (e) {
    document.getElementById("donorCount").textContent =
      "❌ Could not load donors — is Flask running?";
    console.error(e);
  }
}


// ── LOCATE USER / HOSPITAL ──
function locateMe() {
  if (!navigator.geolocation) {
    alert("Geolocation not supported by your browser.");
    return;
  }

  navigator.geolocation.getCurrentPosition(
    (pos) => {
      const lat = pos.coords.latitude;
      const lon = pos.coords.longitude;

      // Remove previous user marker
      myLocLayer.clearLayers();

      // Add blue dot for user
      L.marker([lat, lon], { icon: blueIcon })
        .addTo(myLocLayer)
        .bindPopup("<b>📍 Your Location</b>")
        .openPopup();

      // Draw 10km radius circle
      L.circle([lat, lon], {
        radius: 10000,
        color: "#1F4E79",
        fillColor: "#1F4E79",
        fillOpacity: 0.05,
        weight: 2,
        dashArray: "6"
      }).addTo(myLocLayer);

      // Pan map to user location
      map.setView([lat, lon], 13);
    },
    () => {
      alert("Could not get your location. Please allow location access.");
    }
  );
}


// ── AUTO LOAD ON PAGE OPEN ──
loadDonors();

// ── AUTO REFRESH every 60 seconds ──
setInterval(loadDonors, 60000);