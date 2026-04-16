function getLocation() {
  const btn = document.getElementById("locationBtn");
  const status = document.getElementById("locationStatus");

  btn.textContent = "Detecting...";
  btn.disabled = true;

  navigator.geolocation.getCurrentPosition(
    (pos) => {
      document.getElementById("latitude").value  = pos.coords.latitude;
      document.getElementById("longitude").value = pos.coords.longitude;
      status.textContent = `✅ Location captured`;
      status.style.color = "var(--green)";
      btn.textContent = "✅ Location Captured";
    },
    () => {
      status.textContent = "❌ Location denied. Matching will use city-wide search.";
      btn.textContent = "📍 Capture Hospital Location";
      btn.disabled = false;
    }
  );
}

async function postEmergency() {
  const btn = document.getElementById("submitBtn");
  const successMsg = document.getElementById("successMsg");
  const errorMsg = document.getElementById("errorMsg");

  successMsg.classList.remove("show");
  errorMsg.classList.remove("show");

  const data = {
    requester_name:   document.getElementById("requester_name").value.trim(),
    requester_phone:  document.getElementById("requester_phone").value.trim(),
    blood_group:      document.getElementById("blood_group").value,
    units_needed:     parseInt(document.getElementById("units_needed").value),
    hospital_name:    document.getElementById("hospital_name").value.trim(),
    hospital_address: document.getElementById("hospital_address").value.trim(),
    additional_notes: document.getElementById("additional_notes").value.trim(),
    latitude:         document.getElementById("latitude").value || null,
    longitude:        document.getElementById("longitude").value || null
  };

  if (!data.requester_name || !data.requester_phone || !data.blood_group || !data.hospital_name) {
    errorMsg.textContent = "❌ Please fill all required fields marked with *";
    errorMsg.classList.add("show");
    return;
  }

  btn.innerHTML = '<span class="loader"></span> Alerting donors...';
  btn.disabled = true;

  try {
    const result = await RequestAPI.postEmergency(data);

    if (result.success) {
      successMsg.textContent = "✅ " + result.message;
      successMsg.classList.add("show");

      // Show status box
      document.getElementById("requestId").textContent = result.data.request_id;
      document.getElementById("donorsAlerted").textContent = result.data.donors_alerted + " donors";
      document.getElementById("statusBox").classList.add("show");

      // Scroll to status box
      document.getElementById("statusBox").scrollIntoView({ behavior: "smooth" });
    } else {
      const msg = Array.isArray(result.message) ? result.message.join(", ") : result.message;
      errorMsg.textContent = "❌ " + msg;
      errorMsg.classList.add("show");
    }
  } catch (e) {
    errorMsg.textContent = "❌ Could not connect to server. Is Flask running?";
    errorMsg.classList.add("show");
  }

  btn.innerHTML = "🚨 Alert Nearby Donors Now";
  btn.disabled = false;
}