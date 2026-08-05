/*
 * LoadBalancer.cc
 *
 *  Created on: Aug 5, 2026
 *      Author: opp_env
 */

#include "LoadBalancer.h"
#include "Job_m.h"

Define_Module(LoadBalancer);

void LoadBalancer::handleMessage(cMessage *msg)
{
    int numberOfServers = par("numberOfServers");

    Job *job = check_and_cast<Job *>(msg);
    job->setServerArrivalTime(simTime());

    EV << "Sending job " << job->getJobId()
       << " to server " << nextServer << "\n";

    send(job, "out", nextServer);

    nextServer = (nextServer + 1) % numberOfServers;
}
