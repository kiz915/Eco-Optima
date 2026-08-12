# EcoOptima — Smart Campus Resource Optimizer

> **HackZen'26 Hackathon Submission**  
> *Turning raw building telemetry into computational resource decisions.*

EcoOptima is an automated resource optimization system designed to eliminate energy, cost, and water waste across campus facilities. By analyzing hourly building telemetry, EcoOptima detects operational inefficiencies and formulates linear programming models to compute optimal equipment operating schedules—ensuring occupant comfort while minimizing utility expenses.

---

## 🏗 Technology Stack

- **Backend / API:** Python 3.14, FastAPI, Pydantic v2, Pandas (CSV persistence), `PuLP` (Linear Programming CBC solver), `requests` (Wolfram Alpha API integration), `python-dotenv`.
- **Frontend / UI:** React 19, TypeScript, Vite, Axios, React Router v7, Recharts, Vanilla CSS Design System (Slate/Emerald dark theme).
- **Optimization Engines:**
  1. **Primary Solver:** Wolfram Alpha API (`LinearProgramming[]` / query interface) when network connectivity is live.
  2. **Fallback Solver:** PuLP (CBC Solver) executing a 24-hour constrained linear program locally in Python.

---

## ⚡ Quick Start & Local Execution

### Prerequisites
- **Python:** 3.10+ (tested on Python 3.14)
- **Node.js:** v18+ (tested on Node 24)

### 1. Start the Backend Server

```bash
cd backend

# Install Python dependencies
py -3 -m pip install fastapi uvicorn pydantic python-dotenv PuLP requests pandas

# Launch FastAPI application (runs on http://localhost:8000)
py -3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

*Interactive API documentation is available at:* `http://localhost:8000/docs`

### 2. Start the Frontend Application

```bash
cd frontend

# Install Node dependencies
npm install

# Launch Vite development server (runs on http://localhost:5173)
npm run dev
```

Open **`http://localhost:5173`** in your browser to interact with the application.

---

## 📜 Mandatory Disclaimer

> *"Results are model-based estimates and depend on input data, equipment characteristics, and implementation conditions."*

---

## 🎤 5-Minute Pitch & Demo Script (HackZen'26 Alignment)

### 0. Alignment Check Before Pitch
> **Pre-Pitch Rule:** Check the solver badge on Screen 3 (`solver_used`). If the live Wolfram API key succeeded, state *"Powered by Wolfram Alpha"*. If network latency or API rate limits triggered the fallback, state *"Powered by our local PuLP CBC solver"*. Both are valid; honesty maintains judge credibility.

---

### Minute 0:00 – 0:30 | 1. Problem & Context (Slide 2)
> *"Good morning judges. Campus facilities lose millions of rupees every year through unmonitored equipment usage—like AC units running at 90% capacity overnight in empty buildings. Existing BMS tools show data graphs, but they don't tell facility managers how to fix the waste. EcoOptima bridge this gap by converting telemetry into automated, optimal operational schedules."*

---

### Minute 0:30 – 1:00 | 2. Facility Input (Slide 8)
> *"Here is the EcoOptima Facility Input screen. Facility managers can register building parameters and detailed equipment inventories—such as AC units, lighting fixtures, and water pumps—along with their power ratings and operational bounds.*  
> *For today's demonstration, I'll click **'⚡ Use Demo Facility'** to immediately load pre-seeded telemetry for **Hostel Block A**."*  
> *(Action: Click "⚡ Use Demo Facility" button)*

---

### Minute 1:00 – 2:00 | 3. Telemetry & Waste Detection (Slide 8)
> *"We are now on the **Dashboard**. At the top, you see the 24-hour energy and occupancy trend graph.*  
> *Notice our rule-based waste detection engine flagged 3 operational anomalies below:*  
> 1. **High Severity:** AC running at full power during low occupancy between 23:00 and 05:00, where energy stayed above 48 kWh/hr despite occupancy dropping below 12%.  
> 2. **High Severity:** Nighttime energy consumption baseline significantly exceeds the expected setback mode.  
> 3. **Medium Severity:** Water consumption spiking to 454 L at 02:00 AM—indicating an automated irrigation timer misaligned with building usage.*  
> *Let's now generate an optimal operational schedule to eliminate this waste."*  
> *(Action: Click "⚡ Optimize Now" button)*

---

### Minute 2:00 – 3:30 | 4. Optimization Engine & Honest Solver Verification (Slides 4, 6, 7)
> *"This brings us to the **Optimization Result** screen.*  
> *Behind the scenes, EcoOptima formulates a 24-block Linear Program. Our objective function minimizes total electricity cost subject to strict comfort constraints: whenever occupancy exceeds 50%, AC and lighting are locked to a minimum 70% service floor—ensuring we never 'win' by simply shutting down the building.*  
> *Notice the top-right corner badge:* **`[Solved via Wolfram Alpha]`** *(or `[Solved via local fallback solver]`). It transparently reports the active engine.*  
> *The model achieves a **62.1% monthly cost reduction**—saving **₹144,514** and **17,000 kWh** every month while preserving full service during peak hours."*

---

### Minute 3:30 – 4:30 | 5. Interactive What-If Simulation (Slide 5 Bonus)
> *"EcoOptima is also an interactive decision-support system. Using our **What-If Simulation Panel**, facility managers can adjust real-time parameters.*  
> *Watch what happens if ambient temperature rises to 38°C or occupancy spikes: the model re-evaluates constraints in real time via our `/api/simulate` endpoint and recalculates optimal load setpoints instantly."*  
> *(Action: Adjust Occupancy and Temperature sliders)*

---

### Minute 4:30 – 5:00 | 6. Conclusion & Scalability (Slide 5 & 9)
> *"EcoOptima is not just a passive monitoring dashboard—it is a computational decision-support engine that turns raw telemetry into actionable, cost-saving operational commands. Thank you, and we welcome your questions."*
