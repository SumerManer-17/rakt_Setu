let currentPhone = "";

async function loadProfile() {
  const phone = document.getElementById("lookupPhone").value.trim();
  const errorEl = document.getElementById("lookupError");
  errorEl.classList.remove("show");

  if (!phone || phone.length !== 10) {
    errorEl.textContent = "Please enter a valid 10-digit mobile number";
    errorEl.classList.add("show");
    return;
  }

  try {
    const result = await DonorAPI.getProfile(phone);

    if (!result.success) {
      errorEl.textContent = "❌ " + result.message;
      errorEl.classList.add("show");
      return;
    }

    currentPhone = phone;
    const d = result.data;

    document.getElementById("donorName").textContent    = d.name;
    document.getElementById("donorPhone").textContent   = "+91 " + d.phone;
    document.getElementById("donorBlood").textContent   = d.blood_group;
    document.getElementById("totalDonations").textContent = d.total_donations;
    document.getElementById("donorFreshness").textContent = d.freshness;
    document.getElementById("nextEligible").textContent  = d.eligibility.next_eligible_date;

    const daysLeft = d.eligibility.days_until_eligible;
    document.getElementById("daysUntilEligible").textContent = daysLeft === 0 ? "✅ Now" : daysLeft;

    const statusEl = document.getElementById("donorStatus");
    const toggleBtn = document.getElementById("toggleBtn");
    if (d.is_active) {
      statusEl.innerHTML = '<span class="badge badge-active">Active</span>';
      toggleBtn.textContent = "Pause My Availability";
    } else {
      statusEl.innerHTML = '<span class="badge badge-inactive">Inactive</span>';
      toggleBtn.textContent = "Reactivate My Profile";
    }

    // Donation history
    const historyEl = document.getElementById("historyContent");
    if (d.donation_history && d.donation_history.length > 0) {
      historyEl.innerHTML = `
        <table>
          <tr>
            <th>Date</th>
            <th>Hospital</th>
          </tr>
          ${d.donation_history.map(h => `
            <tr>
              <td>${new Date(h.donated_on).toLocaleDateString("en-IN")}</td>
              <td>${h.hospital || "—"}</td>
            </tr>
          `).join("")}
        </table>
      `;
    }

    document.getElementById("profileSection").style.display = "block";
    document.getElementById("lookupCard").style.display = "none";

  } catch (e) {
    errorEl.textContent = "❌ Could not connect to server.";
    errorEl.classList.add("show");
  }
}

async function toggleStatus() {
  if (!currentPhone) return;
  const result = await DonorAPI.toggleStatus(currentPhone);
  if (result.success) {
    alert(result.message);
    loadProfile();
  }
}