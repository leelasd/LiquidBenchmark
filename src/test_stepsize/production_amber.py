from simtk.openmm import app
import simtk.openmm as mm
from simtk import unit as u
import sys

timestep = float(sys.argv[1]) * u.femtoseconds

cas = "126492-54-4"

target_length = 200 * u.nanoseconds

n_steps = int(target_length / timestep)
output_frequency = int(250 * u.femtoseconds /  timestep)
barostat_frequency = int(25 * u.femtoseconds /  timestep)

print(n_steps, output_frequency, barostat_frequency)

friction = 1.0 / u.picoseconds
temperature = 300. * u.kelvin
pressure = 1.0 * u.atmospheres

cutoff = 0.95 * u.nanometers

prmtop_filename = "./input/126492-54-4_1000_300.6.prmtop"  # cp ~/src/kyleabeauchamp/LiquidBenchmark/liquid_benchmark_3_14/tleap/126492-54-4_1000_300.6.prmtop  ./
pdb_filename = "./input/126492-54-4_1000_300.6_equil.pdb"  # cp ~/src/kyleabeauchamp/LiquidBenchmark/liquid_benchmark_3_14/equil/126492-54-4_1000_300.6_equil.pdb ./

log_filename = "./production/production_%0.2f.log" % (timestep / u.femtoseconds)


pdb = app.PDBFile(pdb_filename)
prmtop = app.AmberPrmtopFile(prmtop_filename)

system = prmtop.createSystem(nonbondedMethod=app.PME, nonbondedCutoff=cutoff, constraints=app.HBonds)

integrator = mm.LangevinIntegrator(temperature, friction, timestep)
system.addForce(mm.MonteCarloBarostat(pressure, temperature, barostat_frequency))

simulation = app.Simulation(prmtop.topology, system, integrator)

simulation.context.setPositions(pdb.positions)
simulation.context.setPeriodicBoxVectors(*pdb.topology.getPeriodicBoxVectors())
simulation.context.setVelocitiesToTemperature(temperature)

simulation.step(10000)

simulation.reporters.append(app.StateDataReporter(open(log_filename, 'w'), output_frequency, step=True, time=True, speed=True, density=True))
simulation.step(n_steps)
