#!/bin/sh

export PATH=$PATH:/app/node_modules/.bin

npm install
npm run dev -- --host 0.0.0.0
