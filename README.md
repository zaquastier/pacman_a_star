# Pac-Man A*-based Game Solver

## Overview

This project is a terminal-based Pac-Man-like game where the gameplay logic is controlled by bots utilizing the A* algorithm. The primary goal is to develop bots that either play as Pac-Man to collect all prizes or as enemies to chase down Pac-Man. The game was developed as part of the MSc IASD program at Université Paris-Dauphine, PSL.

## Gameplay

In this game, the player controls Pac-Man, represented by @, moving through a maze to collect prizes (.) while avoiding enemies (#). The game progresses through multiple levels, each loaded from map files.

### Entities

* @: Player (Pac-Man). Can move horizontally or vertically, eat prizes, and consume powers.
* #: Enemy (Ghost). Chases Pac-Man.
* .: Prize (Dot). Increases score by 1 when collected.
* O: Power (Round Ball). Makes enemies vulnerable and increases score by 5 when collected.
* &: Scared Enemy. Can be eaten by Pac-Man, increasing score by 10.
* H: House. Scared enemies go here to return to normal.
* %: Wall. Impassable barrier.

### Status Codes:

* PRIZE=0: Code for collecting a prize.
* WON=1: Code for winning the level.
* OK=2: Code for a normal move.
* SCORE=3: Code for scoring points.
* LOST=4: Code for losing a life or the game.
* POWER=5: Code for activating a power-up.
* NORMAL=6: Code for normal status.
* EAT=7: Code for eating an enemy.

## Game Implementation

The game runs at a certain frames-per-second rate, with the player moving at each frame while enemies move every few frames. The main logic for pathfinding and game rules is encapsulated in Python classes and functions.

## Usage

### Requirements

Install the required Python packages by running:

``` pip install -r requirements.txt ```

### Running the Game

To start the game, execute the following command:

```
python pacman.py
```

### Use of the curses Library

The game relies on the curses library for terminal handling. If you encounter issues with curses, set `CURSES=False` in config.py to disable curses and run the game in a simpler mode.

## Implementation Details

### Pathfinding

The A* algorithm is used for pathfinding, with custom heuristics to guide the player towards prizes while avoiding enemies, and to guide enemies towards the player or the house when they are scared.

### Player Bot

The player bot calculates the distance to various objects and selects the closest one to eat. When enemies are nearby, a penalization term is added to the distance calculation to avoid them. The path is recalculated every frame to avoid collisions with moving enemies.

### Enemy Bot

Enemies use the A* algorithm to chase Pac-Man. When they are scared, they navigate towards the house to revert to their normal state.

## Maps
Game levels are stored as text files in the maps/levels directory. Each map file represents a level in the game.

## Authors
David Valdivia
Michel Huang
MSc IASD, Université Paris-Dauphine, PSL (2023-2024)