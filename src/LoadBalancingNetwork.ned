//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with this program.  If not, see http://www.gnu.org/licenses/.
//

package src;

network LoadBalancingNetwork
{
    parameters:
        int numberOfServers = default(2);

    submodules:
        generator: JobGenerator {
            parameters:
                generationInterval = default(2s);
                numberOfJobs = default(10);
        }

        loadBalancer: LoadBalancer {
            parameters:
                numberOfServers = parent.numberOfServers;
        }

        server[numberOfServers]: Server {
            parameters:
                serviceTime = default(1s);
        }

    connections:
        generator.out --> loadBalancer.in;

        for i=0..numberOfServers-1 {
            loadBalancer.out[i] --> server[i].in;
        }
}