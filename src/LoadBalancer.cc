/*
 * LoadBalancer.cc
 *
 *  Created on: Aug 5, 2026
 *      Author: opp_env
 */

#include "LoadBalancer.h"

Define_Module(LoadBalancer);

void LoadBalancer::handleMessage(cMessage *msg)
{
    int numberOfServers = par("numberOfServers");

    EV << "Sending " << msg->getName()
       << " to server " << nextServer << "\n";

    send(msg, "out", nextServer);

    nextServer = (nextServer + 1) % numberOfServers;
}
