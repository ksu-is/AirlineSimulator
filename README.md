# Airport Operations Simulator

A fast-paced airport gate management game built with Python and tkinter. Manage incoming flights and assign them to the correct gates during your 8-hour shift!

### Objective
Survive a full 8-hour shift (9 AM - 5 PM) by correctly assigning flights to gates within 3 seconds.

### Rules
- **Terminal A **: Narrowbody aircraft → Domestic destinations only
- **Terminal B **: Widebody aircraft → International destinations only
- You have **3 seconds** to assign each flight to the correct gate
- Occupied gates are disabled and show the flight number

### Lives System
- **Start with 3 lives**: ❤️❤️❤️
- **Wrong aircraft type**: Lose 1 life 💔
- **Timeout (3 seconds)**: Lose 1 life 💔
- **Lose all lives**: Game Over!

### Scoring System
- **Narrowbody correct**: +10 points
- **Widebody correct**: +20 points
- **Score is for bragging rights only** - doesn't affect game over

### Win/Lose Conditions
- **Win**: Complete your shift (reach 5 PM) with lives remaining
- **Lose**: Lose all 3 lives

## Getting Started

### Requirements
- Python 3.x
- tkinter

## Game Features

- **Time-based gameplay**: Real-time clock progression (9 AM - 5 PM)
- **Visual feedback**: Plane emojis, gate colors, departure notifications
- **Automatic departures**: Planes depart after 5-20 seconds
- **Balanced difficulty**: 60% narrowbody, 40% widebody flight distribution
- **13 gates total**: 8 narrowbody (A1-A8), 5 widebody (B1-B5)

## Aircraft Types 

**Narrowbody**: A320, 737, 757, E175, CRJ900, B717, B321  
**Widebody**: 777, 787, A350, A330, B747, A380, B787

## Destinations

**Domestic** (Narrowbody only): ATL, MSP, DTW, SLC, LAX, JFK, BOS, SEA, DEN, ORD, MIA, MCO, LAS, PHX, SFO, DCA, PDX, SAN, TPA, AUS, RDU, CLT, PHL, BWI

**International** (Widebody only): LHR, CDG, AMS, FCO, BCN, MAD, FRA, MUC, HND, ICN, PVG, HKG, SYD, MEL, GRU, EZE, CUN, PUJ, MEX, YVR, YYZ, LIS, DUB, ZRH

---

*Game designed by Rowan Seskin and Gabrielle Godfrey*
