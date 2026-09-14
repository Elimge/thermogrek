# Phase 10: Physical & Mathematical Simulation Model

## 1. Digital Twin Classification & Conceptual Boundary

Before specifying equations, we must establish the formal academic and industrial classification (Kritzinger et al., 2018):

```
┌─────────────────┐       Manual Data Flow      ┌─────────────────┐
│ Physical Asset  │ --------------------------> │  Digital Model  │
│  (or Simulator) │ <-------------------------- │   (Simulation)  │
└─────────────────┘       Manual Data Flow      └─────────────────┘

┌─────────────────┐     Automated Data Flow     ┌─────────────────┐
│ Physical Asset  │ --------------------------> │ Digital Shadow  │
│  (or Simulator) │ <-------------------------- │ (Telemetry/KPIs)│
└─────────────────┘       Manual Data Flow      └─────────────────┘

┌─────────────────┐     Automated Data Flow     ┌─────────────────┐
│ Physical Asset  │ --------------------------> │  Digital Twin   │
│  (or Simulator) │ <-------------------------- │ (Closed-Loop)   │
└─────────────────┘     Automated Data Flow     └─────────────────┘
```

- **Digital Model:** A digital representation with no automated data exchange with the physical asset.
- **Digital Shadow (ThermoGrek MVP):** A digital representation with a **one-way automated data stream** from asset to digital system (telemetry $\to$ MQTT $\to$ KPIs/Health estimation).
- **Digital Twin (Full Stage):** A bidirectional automated loop where digital insights actively control the physical asset (e.g., automatically triggering backwash valves or changing fan VFD speed).

> **Technical Truth for Portfolio:** ThermoGrek MVP is strictly a **Physics-Informed Digital Shadow with Predictive Diagnostics**. We do not make misleading marketing claims of a "Full Closed-Loop Digital Twin".

---

## 2. Shell & Tube Heat Exchanger Model (HE-01)

### 2.1. Physical Principles & Equations

#### A) Thermal Energy Balance
$$\dot{Q}_{hot} = \dot{m}_{hot} \cdot C_{p,hot} \cdot (T_{hot,in} - T_{hot,out})$$
$$\dot{Q}_{cold} = \dot{m}_{cold} \cdot C_{p,cold} \cdot (T_{cold,out} - T_{cold,in})$$

- **Units:**
  - $\dot{Q}$: Heat transfer rate ($\text{kW}$).
  - $\dot{m}$: Mass flow rate ($\text{kg/s}$).
  - $C_p$: Specific heat capacity ($\text{kJ/kg}\cdot\text{K}$). Water: $\approx 4.184\text{ kJ/kg}\cdot\text{K}$; Process Oil: $\approx 2.0\text{ kJ/kg}\cdot\text{K}$.
  - $T$: Temperature in $^\circ\text{C}$.

#### B) Overall Heat Transfer & LMTD (Log Mean Temperature Difference)
$$\dot{Q} = U \cdot A \cdot \text{LMTD} \cdot F$$
$$\text{LMTD} = \frac{\Delta T_1 - \Delta T_2}{\ln\left(\frac{\Delta T_1}{\Delta T_2}\right)}$$
Where for counter-current flow:
- $\Delta T_1 = T_{hot,in} - T_{cold,out}$
- $\Delta T_2 = T_{hot,out} - T_{cold,in}$
- $F$: Geometry correction factor ($F \approx 0.95$ for 1 shell pass, 2 tube passes).
- $A$: Total heat transfer area ($m^2$).
- $U$: Overall heat transfer coefficient ($\text{W}/m^2\cdot\text{K}$).

#### C) Thermal Fouling Resistance ($R_f$)
As scaling accumulates on tube walls, an additional conductive resistance degrades $U$:
$$\frac{1}{U(t)} = \frac{1}{U_{clean}} + R_f(t)$$
Where $R_f(t)$ is the progressive fouling factor ($m^2\cdot\text{K/W}$).

#### D) Hydraulic Degradation (Pressure Drop $\Delta P$)
Hydraulic loss through tube bundles obeys the Darcy-Weisbach formulation:
$$\Delta P = f \cdot \frac{L}{D_i} \cdot \frac{\rho v^2}{2} \propto k \cdot \frac{\dot{V}^2}{D_i^5}$$
As foulant thickness $\delta(t)$ grows:
- Effective inner diameter shrinks: $D_{eff}(t) = D_i - 2\delta(t)$
- Pressure drop increases sharply:
$$\Delta P(t) = \Delta P_{clean} \cdot \left(\frac{D_i}{D_{eff}(t)}\right)^5 \cdot \left(\frac{\dot{V}}{\dot{V}_{design}}\right)^2$$

### 2.2. Model Assumptions & Simplifications
1. Specific heat capacity $C_p$ and density $\rho$ are evaluated at mean bulk temperature and assumed quasi-constant over small operational ranges.
2. Heat loss from the outer insulated shell to the surrounding ambient air is assumed negligible ($\dot{Q}_{hot} \approx \dot{Q}_{cold}$).
3. Flow is assumed fully developed turbulent regime.

### 2.3. Industrial Differences (MVP vs High-Fidelity Simulation)
In a real CFD or Aspen HYSYS simulation, fluid viscosity varies continuously across tube boundary layers, and fouling is non-uniform along the tube length. Our lumped-parameter model captures the exact macroscopic symptoms ($\Delta P$ increase and $U$ decay) without requiring solving Navier-Stokes differential equations.

---

## 3. Cooling Tower Model (CT-01)

### 3.1. Psychrometric Baseline: Stull's Wet-Bulb Temperature ($T_{wb}$)
The theoretical cooling limit of an evaporative cooling tower is the ambient **Wet-Bulb Temperature ($T_{wb}$)**. It is calculated from Dry-Bulb Temperature ($T_{db}$ in $^\circ\text{C}$) and Relative Humidity ($RH$ in $\%$) using Stull's empirical psychrometric approximation:

$$T_{wb} = T_{db} \cdot \arctan\left(0.151977 \cdot (RH + 8.313659)^{0.5}\right) + \arctan(T_{db} + RH) - \arctan(RH - 1.676331) + 0.00391838 \cdot (RH)^{1.5} \cdot \arctan(0.023101 \cdot RH) - 4.686035$$

*(Valid for $RH$ between $1\%$ and $99\%$ and $T_{db}$ between $-20^\circ\text{C}$ and $50^\circ\text{C}$ with mean absolute error $< 0.3^\circ\text{C}$).*

### 3.2. Cooling Tower Performance Indicators

#### A) Cooling Range ($\Delta T_{water}$)
$$\text{Range} = T_{water,in} - T_{water,out}$$

#### B) Approach Temperature
$$\text{Approach} = T_{water,out} - T_{wb}$$
- **Physical Meaning:** A clean, well-operating industrial cooling tower typically achieves an Approach between $3^\circ\text{C}$ and $6^\circ\text{C}$.
- **Degradation Indicator:** As nozzle distribution clogs or fill surface calcifies, Approach drifts upward ($> 8^\circ\text{C}-10^\circ\text{C}$).

#### C) Tower Effectiveness ($\eta_{CT}$)
$$\eta_{CT} = \frac{\text{Range}}{\text{Range} + \text{Approach}} = \frac{T_{water,in} - T_{water,out}}{T_{water,in} - T_{wb}} \cdot 100\%$$

---

## 4. Progressive Fouling Degradation Profile

The simulator implements a deterministic degradation schedule across simulated operational days:

| Simulated Stage | Operational Days | Fouling Factor $R_f$ ($m^2\cdot\text{K/kW}$) | $\Delta P$ Multiplier | Health Index | Classification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Stage 0: Clean** | Day 1 - 15 | $0.00$ | $1.00 \times \Delta P_{nom}$ | $100\% - 95\%$ | `NORMAL` |
| **Stage 1: Incipient** | Day 16 - 35 | $0.15$ | $1.15 \times \Delta P_{nom}$ | $94\% - 85\%$ | `NORMAL` |
| **Stage 2: Moderate** | Day 36 - 55 | $0.35$ | $1.35 \times \Delta P_{nom}$ | $84\% - 70\%$ | `WARNING_FOULING_INCIPIENT` |
| **Stage 3: Severe** | Day 56 - 75 | $0.65$ | $1.70 \times \Delta P_{nom}$ | $69\% - 50\%$ | `WARNING_FOULING_INCIPIENT` |
| **Stage 4: Critical** | Day 76+ | $\ge 1.00$ | $> 2.10 \times \Delta P_{nom}$ | $< 50\%$ | `CRITICAL_MAINTENANCE_REQUIRED` |
