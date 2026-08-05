/*
 * Server.cc
 *
 *  Created on: Aug 5, 2026
 *      Author: opp_env
 */

#include "Server.h"
#include "Job_m.h"

Define_Module(Server);

void Server::initialize()
{
    serviceCompletionEvent = new cMessage("serviceCompletionEvent");

    responseTimeSignal = registerSignal("responseTime");
    waitingTimeSignal = registerSignal("waitingTime");
    queueLengthSignal = registerSignal("queueLength");
}

void Server::handleMessage(cMessage *msg)
{
    if (msg == serviceCompletionEvent) {
        simtime_t responseTime =
            simTime() - currentJob->getCreationTime();

        emit(responseTimeSignal, responseTime);

        EV << "Completed " << currentJob->getName()
           << " at time " << simTime()
           << ", response time = " << responseTime << "\n";

        totalBusyTime += simTime() - serviceStartTime;

        delete currentJob;
        currentJob = nullptr;

        if (!queue.isEmpty()) {
            cMessage *nextJob =
                check_and_cast<cMessage *>(queue.pop());

            startService(nextJob);
        }
    }
    else {
        if (currentJob == nullptr) {
            startService(msg);
        }
        else {
            queue.insert(msg);

            emit(queueLengthSignal, queue.getLength());

            EV << "Queued " << msg->getName()
               << ", queue length = "
               << queue.getLength() << "\n";
        }
    }
}

void Server::startService(cMessage *job)
{
    currentJob = job;
    serviceStartTime = simTime();

    Job *typedJob = check_and_cast<Job *>(job);

    simtime_t waitingTime =
        simTime() - typedJob->getServerArrivalTime();

    emit(waitingTimeSignal, waitingTime);
    emit(queueLengthSignal, queue.getLength());

    simtime_t duration = par("serviceTime");

    EV << "Starting service for job "
       << typedJob->getJobId()
       << " at time " << simTime()
       << ", waiting time = " << waitingTime
       << ", service duration = " << duration << "\n";

    scheduleAt(simTime() + duration, serviceCompletionEvent);
}

void Server::finish()
{
    if (currentJob != nullptr) {
        totalBusyTime += simTime() - serviceStartTime;
    }

    double utilization = 0;

    if (simTime() > SIMTIME_ZERO) {
        utilization =
            totalBusyTime.dbl() / simTime().dbl();
    }

    recordScalar("utilization", utilization);
    recordScalar("completedQueueLength", queue.getLength());

    cancelAndDelete(serviceCompletionEvent);
    serviceCompletionEvent = nullptr;

    delete currentJob;
    currentJob = nullptr;

    while (!queue.isEmpty()) {
        delete check_and_cast<cMessage *>(queue.pop());
    }
}
