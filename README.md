# Predict.LoL - Match Prediction System

![League of Legends Prediction System](https://via.placeholder.com/800x400?text=Predict.LoL+Screenshot)

## Overview

This application predicts the outcome of League of Legends matches using player performance metrics. Originally developed in Python, it now features a web interface with enhanced algorithms for more accurate predictions.

## How It Works

### Core Prediction Flow

1. **Match Input** → Accepts live match IDs or draft compositions  
2. **Player Analysis** → Fetches current player statistics  
3. **SR Calculation** → Computes Summoner Rating for each player  
4. **Team Comparison** → Aggregates ratings and predicts outcome  
5. **Visualization** → Displays prediction with confidence percentage  

### Key Components

| Component | Description |
|-----------|-------------|
| Summoner Rating (SR) | Quantitative measure of player impact |
| Match Analyzer | Processes live match data from Riot API |
| Prediction Engine | Compares team compositions using SR metrics |
| Result Visualizer | Generates Discord/Web-friendly output |

## Summoner Rating (SR) Calculation

The SR algorithm evaluates players across four key dimensions:

## SR Calculation Formula

\[ SR = \left\lfloor 5(s(T) + 0.2R) + \frac{TD}{175} + \left( \frac{10K}{D} + \frac{2A}{D} \right) + \frac{CS}{50} \right\rfloor \]

Where:
- \( s(T) \) = Tier score (CHALLENGER=32, GRANDMASTER=24, etc.)
- \( R \) = Roman numeral rank conversion (I=4, IV=1)
- \( TD \) = Average tower damage
- \( K \) = Average kills
- \( D \) = Average deaths
- \( A \) = Average assists
- \( CS \) = Average creep score

### 1. Rank Bonus (50-75% weight)

**Variables:**  
- T: Player tier (e.g., "CHALLENGER")  
- LP: League Points (0-1000+)  
- R: Rank converted from Roman numerals (I=4, IV=1)  

**Tier Scores:**  
| Tier        | Score |
|-------------|-------|
| CHALLENGER  | 32    |
| GRANDMASTER | 24    |
| MASTER      | 20    |
| DIAMOND     | 14    |
| EMERALD     | 10    |
| PLATINUM    | 7     |
| GOLD        | 4     |
| SILVER      | 3     |
| BRONZE      | 2     |
| IRON        | 1     |

### 2. Tower Damage Bonus (5-15% weight)

### 3. KDA Rating (20-40% weight)

### 4. CS Bonus (5-15% weight)

## Prediction Methodology

### Team SR Sum

### Win Probability

### Confidence Thresholds
- ≤45%: Very Low Confidence  
- 45-55%: Low Confidence  
- 55-70%: Medium Confidence  
- ≥70%: High Confidence  

## Future Development

### Planned Features
- Pro match prediction module  
- Fantasy league integration  
- Real-time draft analyzer  
- Mobile application  

### Optimization Goals
1. Reduce API call latency  
2. Improve SR calculation for support roles  
3. Add champion-specific modifiers  
4. Implement machine learning refinement  