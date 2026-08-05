/*
 * LoadBalancer.h
 *
 *  Created on: Aug 5, 2026
 *      Author: opp_env
 */

#ifndef SRC_LOADBALANCER_H_
#define SRC_LOADBALANCER_H_

#include <omnetpp.h>

using namespace omnetpp;

class LoadBalancer : public cSimpleModule
{
  private:
    int nextServer = 0;

  protected:
    virtual void handleMessage(cMessage *msg) override;
};

#endif /* SRC_LOADBALANCER_H_ */
