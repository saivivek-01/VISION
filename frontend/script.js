const form = document.getElementById("uploadForm");
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const file = document.getElementById("fileInput").files[0];
  const status = document.getElementById("status");

  if (!file) {
    status.innerText = "Please select a file.";
    return;
  }

  status.classList.remove("hidden");
  status.innerText = " Uploading file...";

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("/upload", {
      method: "POST",
      body: formData
    });
    const data = await res.json();

    if (data.filename) {
      localStorage.setItem("uploaded_filename", data.filename);
      window.location.href = "/conversion_options.html";
    } else {
      throw new Error(data.error || "Upload failed.");
    }
  } catch (err) {
    status.innerText = " Error: " + err.message;
  }
});

