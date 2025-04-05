# FediAI

This repository contains the components for a decentralized AI infrastructure on the Fediverse ([FediAI Paper](https://github.com/bluebbberry/FediAI/wiki/FediAI%E2%80%90Paper)).
It's based on Message Queues, mapping hashtags on topics and routing tasks over hashtags, and AI workers.

It consists of the following three parts:

- **Main-App:** chat interface, with which the user can send requests to the fediverse
- **FediAI-Worker:** listens to hashtags and replies to requests send by FediAI-main-app 
