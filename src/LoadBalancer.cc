/*
 * LoadBalancer.cc
 *
 *  Created on: Aug 5, 2026
 *      Author: opp_env
 */

#include "LoadBalancer.h"
#include "Job_m.h"
#include "Server.h"
#include <string>

Define_Module(LoadBalancer);

void LoadBalancer::handleMessage(cMessage *msg)
{
    int numberOfServers = par("numberOfServers");
    std::string algorithm = par("algorithm").stdstringValue();

    int selectedServer = 0;

    if (algorithm == "roundRobin") {
        selectedServer = nextServer;
        nextServer = (nextServer + 1) % numberOfServers;
    }
    else if (algorithm == "random") {
        selectedServer = intuniform(0, numberOfServers - 1);
    }
    else if (algorithm == "shortestQueue") {
        selectedServer = chooseShortestQueue(numberOfServers);
    }
    else if (algorithm == "powerOfTwo") {
        selectedServer = choosePowerOfTwo(numberOfServers);
    }
    else {
        throw cRuntimeError(
            "Unknown load balancing algorithm: %s",
            algorithm.c_str()
        );
    }

    Job *job = check_and_cast<Job *>(msg);
    job->setServerArrivalTime(simTime());

    EV << "Sending job " << job->getJobId()
       << " to server " << selectedServer
       << " using " << algorithm << "\n";

    send(job, "out", selectedServer);
}


int LoadBalancer::getServerLoad(int serverIndex)
{
    cGate *destinationGate =
        gate("out", serverIndex)->getPathEndGate();

    Server *server =
        check_and_cast<Server *>(
            destinationGate->getOwnerModule()
        );

    return server->getSystemLength();
}


int LoadBalancer::chooseShortestQueue(int numberOfServers)
{
    int bestServer = 0;
    int bestLoad = getServerLoad(0);
    int numberOfTies = 1;

    for (int i = 1; i < numberOfServers; i++) {
        int load = getServerLoad(i);

        if (load < bestLoad) {
            bestServer = i;
            bestLoad = load;
            numberOfTies = 1;
        }
        else if (load == bestLoad) {
            numberOfTies++;

            if (intuniform(1, numberOfTies) == 1) {
                bestServer = i;
            }
        }
    }

    return bestServer;
}


int LoadBalancer::choosePowerOfTwo(int numberOfServers)
{
    if (numberOfServers == 1) {
        return 0;
    }

    int first =
        intuniform(0, numberOfServers - 1);

    int second;

    do {
        second =
            intuniform(0, numberOfServers - 1);
    }
    while (second == first);

    int firstLoad = getServerLoad(first);
    int secondLoad = getServerLoad(second);

    if (firstLoad < secondLoad) {
        return first;
    }

    if (secondLoad < firstLoad) {
        return second;
    }

    return intuniform(0, 1) == 0? first: second;
}
