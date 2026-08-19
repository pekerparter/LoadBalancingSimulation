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

    simtime_t serviceStartTime;
    simtime_t totalBusyTime = 0;

  protected:
    virtual void initialize() override;
    virtual void handleMessage(cMessage *msg) override;
    virtual void finish() override;

    void startService(cMessage *job);

  public:
      int getSystemLength() const
      {
          return queue.getLength() + (currentJob != nullptr ? 1 : 0);
      }
};

#endif /* SRC_SERVER_H_ */
