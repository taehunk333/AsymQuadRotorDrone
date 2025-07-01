import matplotlib.pyplot as plt
import numpy as np

# PID controller for altitude + attitude hover
class PIDController:
    def __init__(self):
        self.kp_pos = np.array([1.0, 1.0, 15.0])
        self.kd_pos = np.array([2.0, 2.0, 7.0])
        self.kp_ang = np.array([200.0, 200.0, 100.0])
        self.kd_ang = np.array([20.0, 20.0, 10.0])
        self.integral_error_pos = np.zeros(3)
        self.integral_error_ang = np.zeros(3)
        self.last_error_pos = None
        self.last_error_ang = None

    def control(self, t, x, setpoint):
        p = x[0:3]
        v = x[3:6]
        angles = x[6:9]
        omega = x[9:12]

        # Position control (hover at setpoint position)
        error_pos = setpoint[0:3] - p
        error_vel = setpoint[3:6] - v

        # PID on position (no integral term here for brevity)
        u1 = self.kp_pos * error_pos + self.kd_pos * error_vel
        # Desired total thrust in inertial frame:
        thrust_des = u1 + np.array([0,0,9.81])

        # Desired thrust in body frame approximately:
        phi_des = 0
        theta_des = 0
        psi_des = 0

        # Angular errors
        error_ang = np.array([phi_des, theta_des, psi_des]) - angles
        error_omega = -omega

        # Simple PD on angles to desired torque vector
        tau_des = self.kp_ang * error_ang + self.kd_ang * error_omega

        # Compute rotor speeds from thrust and torque demands
        # Build control allocation matrix
        l = np.array([np.linalg.norm(r[:2]) for r in quad.r_pos_rel])
        Lx = np.array([r[0] for r in quad.r_pos_rel])
        Ly = np.array([r[1] for r in quad.r_pos_rel])

        # Allocation matrix B:
        B = np.zeros((4,4))
        B[0,:] = quad.kf  # thrust
        B[1,:] = quad.kf * Ly  # tau_phi
        B[2,:] = -quad.kf * Lx # tau_theta
        B[3,:] = quad.km * quad.rotor_dirs  # tau_psi

        # Desired forces and moments vector
        force_moments = np.array([
            thrust_des[2] * quad.m,  # total thrust (z axis)
            tau_des[0],
            tau_des[1],
            tau_des[2]
        ])

        # Solve for rotor thrust squares
        omega_squared = np.linalg.pinv(B) @ force_moments
        omega_squared = np.clip(omega_squared, 0, None)  # no negative thrust

        omega = np.sqrt(omega_squared)
        return omega

# Define mass distribution (example)
masses_positions = [
    (1.0, np.array([0, 0, 0])),       # body mass at center
    (0.1, np.array([0.15, 0, 0])),    # right arm
    (0.1, np.array([-0.15, 0, 0])),   # left arm
    (0.1, np.array([0, 0.2, 0])),     # front arm
    (0.1, np.array([0, -0.2, 0]))     # rear arm
]

# Rotor positions
rotor_positions = np.array([
    [0.15, 0, 0],
    [-0.15, 0, 0],
    [0, 0.2, 0],
    [0, -0.2, 0]
])

# Motor parameters
kf = np.array([3e-6, 3.1e-6, 2.9e-6, 3e-6])
km = np.array([1e-7, 1.05e-7, 0.95e-7, 1e-7])
rotor_dirs = np.array([1, -1, 1, -1])

# Body inertia (assumed diagonal here)
I_body = np.diag([0.005, 0.005, 0.009])

# Drag matrices
Cd = np.diag([0.1, 0.1, 0.2])
Ctau = np.diag([0.01, 0.01, 0.02])

# Initialize quadrotor
quad = NonSymmetricQuadrotor(rotor_positions, kf, km, masses_positions, I_body, Cd, Ctau, rotor_dirs)

# Initial state (hover at origin)
x0 = np.zeros(12)
t_span = (0, 5)
t_eval = np.linspace(*t_span, 500)

# Controller instance
pid = PIDController()

def omega_func(t, x):
    return pid.control(t, x, np.array([0,0,1,0,0,0]))

# Simulate
sol = quad.simulate(omega_func, x0, t_span, t_eval)

# Plot altitude over time
import matplotlib.pyplot as plt
plt.plot(sol.t, sol.y[2])
plt.xlabel('Time (s)')
plt.ylabel('Altitude (m)')
plt.title('Hover altitude of non-symmetric quadrotor')
plt.grid()
plt.show()