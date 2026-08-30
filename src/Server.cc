/*
 * Server.cc
 *
 *  Created on: Aug 5, 2026
 *      Author: opp_env
 */

#include "Server.h"
#include "Job_m.h"

#include <algorithm>

Define_Module(Server);

void Server::initialize()
{
    serviceCompletionEvent =
        new cMessage("serviceCompletionEvent");

    responseTimeSignal = registerSignal("responseTime");
    waitingTimeSignal = registerSignal("waitingTime");
    queueLengthSignal = registerSignal("queueLength");
    busySignal = registerSignal("busy");

    emit(queueLengthSignal, 0L);
    emit(busySignal, false);

    measurementStart = par("measurementStart");

    measuredBusyTime = SIMTIME_ZERO;
    completedJobs = 0;

    queueArea = 0.0;
    lastQueueChangeTime = SIMTIME_ZERO;
}


void Server::handleMessage(cMessage *msg)
{
    if (msg == serviceCompletionEvent) {

        Job *completedJob =
            check_and_cast<Job *>(currentJob);

        // Add the busy interval of the completed job.
        addBusyInterval(serviceStartTime, simTime());

        // Only use jobs created after the warm-up
        // for response-time and throughput measurements.
        if (completedJob->getCreationTime() >= measurementStart) {

            simtime_t responseTime = simTime() - completedJob->getCreationTime();

            emit(responseTimeSignal, responseTime);

            responseTimeStats.collect(responseTime.dbl());

            completedJobs++;

            EV << "Completed job " << completedJob->getJobId()
               << " at time " << simTime()
               << ", response time = " << responseTime << "\n";
        }
        else {
            EV << "Completed warm-up job " << completedJob->getJobId()
               << " at time " << simTime() << "\n";
        }

        delete currentJob;
        currentJob = nullptr;

        if (!queue.isEmpty()) {

            // Queue length is about to change,
            // so first account for how long it
            // stayed at its previous value.
            updateQueueArea();

            cMessage *nextJob = check_and_cast<cMessage *>(queue.pop());

            emit(queueLengthSignal, queue.getLength());

            startService(nextJob);
        }
        else {
            emit(busySignal, false);
        }
    }

    else {
        Job *job = check_and_cast<Job *>(msg);

        if (currentJob == nullptr) {
            startService(job);
        }
        else {
            updateQueueArea();

            queue.insert(job);

            emit(queueLengthSignal, queue.getLength());

            EV << "Queued job " << job->getJobId()
               << ", queue length = " << queue.getLength() << "\n";
        }
    }
}


void Server::startService(cMessage *job)
{
    currentJob = job;
    serviceStartTime = simTime();

    emit(busySignal, true);

    Job *typedJob =
        check_and_cast<Job *>(job);

    if (typedJob->getServerArrivalTime() >= measurementStart) {

        simtime_t waitingTime =
            simTime() - typedJob->getServerArrivalTime();

        emit(waitingTimeSignal, waitingTime);

        waitingTimeStats.collect(
            waitingTime.dbl()
        );

        EV << "Starting service for job " << typedJob->getJobId()
           << " at time " << simTime()
           << ", waiting time = " << waitingTime;
    }
    else {
        EV << "Starting service for warm-up job " << typedJob->getJobId() << " at time " << simTime();
    }

    simtime_t duration =
        typedJob->getServiceTime();

    EV << ", service duration = "<< duration << "\n";

    scheduleAt(
        simTime() + duration,
        serviceCompletionEvent
    );
}


void Server::addBusyInterval(
    simtime_t start,
    simtime_t end)
{
    // Ignore intervals entirely before measurement.
    if (end <= measurementStart) {
        return;
    }

    simtime_t measuredStart =
        std::max(start, measurementStart);

    measuredBusyTime +=
        end - measuredStart;
}


void Server::updateQueueArea()
{
    simtime_t now = simTime();

    if (now > measurementStart) {

        simtime_t intervalStart =
            std::max(
                lastQueueChangeTime,
                measurementStart
            );

        if (now > intervalStart) {
            double duration =
                (now - intervalStart).dbl();

            queueArea +=
                queue.getLength() * duration;
        }
    }

    lastQueueChangeTime = now;
}


void Server::finish()
{
    // Account for the queue state until the
    // end of the simulation.
    updateQueueArea();

    // If a job is still being processed when
    // the simulation stops, count its busy time
    // up to the end.
    if (currentJob != nullptr) {
        addBusyInterval(
            serviceStartTime,
            simTime()
        );
    }

    simtime_t measurementDuration =
        simTime() - measurementStart;

    double utilization = 0.0;
    double throughput = 0.0;
    double meanQueueLength = 0.0;

    if (measurementDuration > SIMTIME_ZERO) {

        utilization =
            measuredBusyTime.dbl()
            / measurementDuration.dbl();

        throughput =
            completedJobs
            / measurementDuration.dbl();

        meanQueueLength =
            queueArea
            / measurementDuration.dbl();
    }

    recordScalar(
        "utilization",
        utilization
    );

    recordScalar(
        "completedJobs",
        completedJobs
    );

    recordScalar(
        "throughput",
        throughput
    );

    recordScalar(
        "meanQueueLength",
        meanQueueLength
    );

    if (responseTimeStats.getCount() > 0) {
        recordScalar(
            "meanResponseTime",
            responseTimeStats.getMean()
        );

        recordScalar(
            "responseTimeStddev",
            responseTimeStats.getStddev()
        );
    }

    if (waitingTimeStats.getCount() > 0) {
        recordScalar(
            "meanWaitingTime",
            waitingTimeStats.getMean()
        );

        recordScalar(
            "waitingTimeStddev",
            waitingTimeStats.getStddev()
        );
    }

    cancelAndDelete(serviceCompletionEvent);
    serviceCompletionEvent = nullptr;

    delete currentJob;
    currentJob = nullptr;

    while (!queue.isEmpty()) {
        delete check_and_cast<cMessage *>(
            queue.pop()
        );
    }
}



