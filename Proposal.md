# Capstone Project One - Proposal

## Goals

SneakerHeads will be designed to show users current and upcoming shoes from popular brands.  
It will allow users to like and watchlist shoes, and will create recommendations.

## Stretch Goal

Provide price tracking, and notifications for new highs/lows.

## Users

SneakerHeads' target demographic will be any person with an eye on or taste for popular, stylish footwear. Generally speaking, this will be young, affluent professionals/teenagers.

## Data

I plan on using thesneakerapi for general data on shoes:

- release info
- brand info
- product info
- pricing info?
  I am considering webscraping for pricing updates.

## Brief Outline

### a) - Database schema

[Schema Design](crowsfoot.jpeg)

### b) - Possible issues?

Maybe reliability, thesneakerapi's calls and responses are very straightforward otherwise.

### c) - Sensitive info?

User credentials will be encrypted, watchlists will be gated by user.

### d) - Functionality

The site will function a lot like an ecommerce platform with a sortable, filterable list of products at its core. It will include user pages, with lists of favorited items, and a private watchlist page for tracking aftermarket prices.

### e) - User flow

Users will enter the site and be presented with a large product listing.  
Upon logging in, users will gain access to liking, and wathclisting buttons.  
Unauth users/ user without likes will be presented with recommendations based on the product they are viewing
Users with likes/watchlist will get a list of recommendations based on product attributes  
they like most.

### f) More than CRUD

The recommendation system will be what elevates this project beyond basic CRUD
