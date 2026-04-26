# VISION - Visual Interpretation of Scripts Into Organised Narration

## How to Run Locally (macOS)
1. Create virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. Start server:
   ```bash
   cd backend
   python main.py
   ```

4. Upload text/PDF via frontend or Postman to `/generate`.

## Project Structure
- `backend/` - API and core logic
- `frontend/` - Web UI
- `assets/` - Sample inputs and generated outputs
