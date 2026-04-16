function getLocation() {
  const btn = document.getElementById("locationBtn");
  const status = document.getElementById("locationStatus");

  btn.textContent = "Detecting...";
  btn.disabled = true;

  if (!navigator.geolocation) {
    status.textContent = "❌ Geolocation not supported by your browser";
    btn.textContent = "📍 Capture My Location";
    btn.disabled = false;
    return;
  }

  navigator.geolocation.getCurrentPosition(
    (pos) => {
      document.getElementById("latitude").value  = pos.coords.latitude;
      document.getElementById("longitude").value = pos.coords.longitude;
      status.textContent = `✅ Location captured: ${pos.coords.latitude.toFixed(4)}, ${pos.coords.longitude.toFixed(4)}`;
      status.style.color = "var(--green)";
      btn.textContent = "✅ Location Captured";
    },
    (err) => {
      status.textContent = "❌ Location access denied. Please allow location and try again.";
      btn.textContent = "📍 Capture My Location";
      btn.disabled = false;
    }
  );
}

async function registerDonor() {
  const btn = document.getElementById("submitBtn");
  const successMsg = document.getElementById("successMsg");
  const errorMsg = document.getElementById("errorMsg");

  successMsg.classList.remove("show");
  errorMsg.classList.remove("show");

  const data = {
    name:        document.getElementById("name").value.trim(),
    phone:       document.getElementById("phone").value.trim(),
    blood_group: document.getElementById("blood_group").value,
    city:        document.getElementById("city").value.trim(),
    pincode:     document.getElementById("pincode").value.trim(),
    latitude:    document.getElementById("latitude").value || null,
    longitude:   document.getElementById("longitude").value || null
  };

  // Basic frontend validation
  if (!data.name || !data.phone || !data.blood_group || !data.pincode) {
    errorMsg.textContent = "Please fill all required fields marked with *";
    errorMsg.classList.add("show");
    return;
  }

  btn.innerHTML = '<span class="loader"></span> Registering...';
  btn.disabled = true;

  try {
    const result = await DonorAPI.register(data);

    if (result.success) {
      successMsg.textContent = "🎉 " + result.message;
      successMsg.classList.add("show");
      // Clear form
      ["name","phone","blood_group","city","pincode","latitude","longitude"].forEach(id => {
        document.getElementById(id).value = "";
      });
      document.getElementById("locationStatus").textContent = "Location not captured yet";
      document.getElementById("locationStatus").style.color = "var(--gray)";
      document.getElementById("locationBtn").textContent = "📍 Capture My Location";
    } else {
      const msg = Array.isArray(result.message) ? result.message.join(", ") : result.message;
      errorMsg.textContent = "❌ " + msg;
      errorMsg.classList.add("show");
    }
  } catch (e) {
    errorMsg.textContent = "❌ Could not connect to server. Is Flask running?";
    errorMsg.classList.add("show");
  }

  btn.innerHTML = "Register as Donor";
  btn.disabled = false;
}