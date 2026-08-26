#include "JobGenerator.h"
#include "Job_m.h"

Define_Module(JobGenerator);

void JobGenerator::initialize()
{
    generationEvent = new cMessage("generationEvent");

    // Generate the first job at simulation time 0.
    scheduleAt(simTime(), generationEvent);
}

void JobGenerator::handleMessage(cMessage *msg)
{
    if (msg != generationEvent) {
        throw cRuntimeError("JobGenerator received an unexpected message.");
    }

    int numberOfJobs = par("numberOfJobs");

    if (nextJobId >= numberOfJobs) {
        return;
    }

    Job *job = new Job("job");
    job->setJobId(nextJobId);
    job->setCreationTime(simTime());
    job->setServiceTime(par("jobServiceTime"));

    EV << "Generated job " << nextJobId << " at time " << simTime()
       << ", service requirement = " << job->getServiceTime() <<"\n";

    send(job, "out");

    nextJobId++;

    if (nextJobId < numberOfJobs) {
        simtime_t interval = par("generationInterval");
        scheduleAt(simTime() + interval, generationEvent);
    }
}

void JobGenerator::finish()
{
    cancelAndDelete(generationEvent);
    generationEvent = nullptr;
}
