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

simple Server
{
    parameters:
        double measurementStart @unit(s) = default(0s);

        @signal[responseTime](type=simtime_t);
        @signal[waitingTime](type=simtime_t);
        @signal[queueLength](type=long);
        @signal[busy](type=bool);

        @statistic[responseTime](source=responseTime; record=vector);
        @statistic[waitingTime](source=waitingTime; record=vector);
        @statistic[queueLength](source=queueLength; record=vector);
        @statistic[busy](source=busy; record=vector);

    gates:
        input in;
}
