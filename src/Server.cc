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
    serviceCompletionEvent =
        new cMessage("serviceCompletionEvent");

    responseTimeSignal = registerSignal("responseTime");
    waitingTimeSignal = registerSignal("waitingTime");
    queueLengthSignal = registerSignal("queueLength");
}

void Server::handleMessage(cMessage *msg)
{
    if (msg == serviceCompletionEvent) {
        Job *completedJob =
            check_and_cast<Job *>(currentJob);

        simtime_t responseTime =
            simTime() - completedJob->getCreationTime();

        emit(responseTimeSignal, responseTime);

        EV << "Completed job " << completedJob->getJobId()
           << " at time " << simTime()
           << ", response time = "
           << responseTime << "\n";

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
        Job *job = check_and_cast<Job *>(msg);

        if (currentJob == nullptr) {
            startService(job);
        }
        else {
            queue.insert(job);

            emit(queueLengthSignal, queue.getLength());

            EV << "Queued job " << job->getJobId()
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
       << ", service duration = "
       << duration << "\n";

    scheduleAt(
        simTime() + duration,
        serviceCompletionEvent
    );
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
    recordScalar("remainingQueueLength", queue.getLength());

    cancelAndDelete(serviceCompletionEvent);
    serviceCompletionEvent = nullptr;

    delete currentJob;
    currentJob = nullptr;

    while (!queue.isEmpty()) {
        delete check_and_cast<cMessage *>(queue.pop());
    }
}
