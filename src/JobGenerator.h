#ifndef __LOADBALANCINGSIMULATION_JOBGENERATOR_H
#define __LOADBALANCINGSIMULATION_JOBGENERATOR_H

#include <omnetpp.h>

using namespace omnetpp;

class JobGenerator : public cSimpleModule
{
  private:
    cMessage *generationEvent = nullptr;
    int nextJobId = 0;

  protected:
    virtual void initialize() override;
    virtual void handleMessage(cMessage *msg) override;
    virtual void finish() override;
};

#endif
