/*
 * Server.h
 *
 *  Created on: Aug 5, 2026
 *      Author: opp_env
 */

#ifndef SRC_SERVER_H_
#define SRC_SERVER_H_

#include <omnetpp.h>

using namespace omnetpp;

class Server : public cSimpleModule
{
  private:
    cQueue queue;

    cMessage *serviceCompletionEvent = nullptr;
    cMessage *currentJob = nullptr;

    simsignal_t responseTimeSignal;
    simsignal_t waitingTimeSignal;
    simsignal_t queueLengthSignal;
    simsignal_t busySignal;

    simtime_t serviceStartTime;
    simtime_t measurementStart;

    // Statistics for the measurement period only
    simtime_t measuredBusyTime = 0;
    long completedJobs = 0;

    cStdDev responseTimeStats;
    cStdDev waitingTimeStats;

    double queueArea = 0.0;
    simtime_t lastQueueChangeTime = 0;

  protected:
    virtual void initialize() override;
    virtual void handleMessage(cMessage *msg) override;
    virtual void finish() override;

    void startService(cMessage *job);

    void addBusyInterval(simtime_t start, simtime_t end);
    void updateQueueArea();

  public:
    int getSystemLength() const
    {
        return queue.getLength()
             + (currentJob != nullptr ? 1 : 0);
    }
};

#endif /* SRC_SERVER_H_ */
