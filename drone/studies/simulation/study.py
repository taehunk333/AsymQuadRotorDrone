import numpy as np
from scipy.integrate import solve_ivp

class NonSymmetricQuadrotor:
    def __init__(self, rotor_positions, kf, km, masses_positions, I_body, Cd=None, Ctau=None, rotor_dirs=None):
        """
        Parameters:
        rotor_positions: (4,3) array of rotor coords in body frame
        kf: array (4,) thrust coefficients per rotor
        km: array (4,) moment coefficients per rotor
        masses_positions: list of tuples [(m_j, pos_j), ...] for all parts
        I_body: (3,3) inertia tensor of main body at its own CoM
        Cd: (3,3) drag matrix for translational drag
        Ctau: (3,3) drag matrix for rotational drag
        rotor_dirs: (4,) array with 1 or -1 for rotor spin direction
        """
        self.r_pos = np.array(rotor_positions)
        self.kf = np.array(kf)
        self.km = np.array(km)
        self.masses_positions = masses_positions
        self.I_body = np.array(I_body)
        self.Cd = np.array(Cd) if Cd is not None else np.zeros((3,3))
        self.Ctau = np.array(Ctau) if Ctau is not None else np.zeros((3,3))
        self.rotor_dirs = np.array(rotor_dirs) if rotor_dirs is not None else np.array([1,-1,1,-1])

        self.compute_mass_properties()

    def compute_mass_properties(self):
        masses = np.array([m for m, _ in self.masses_positions])
        positions = np.array([pos for _, pos in self.masses_positions])
        total_mass = np.sum(masses)
        self.m = total_mass
        self.CoM = np.sum(masses[:,None] * positions, axis=0) / total_mass

        # Shift all positions relative to CoM
        rel_pos = positions - self.CoM

        # Compute inertia tensor using parallel axis theorem
        I = np.zeros((3,3))
        for m_i, r_i in zip(masses, rel_pos):
            r_cross = np.array([
                [0, -r_i[2], r_i[1]],
                [r_i[2], 0, -r_i[0]],
                [-r_i[1], r_i[0], 0]
            ])
            I += m_i * (np.dot(r_i, r_i) * np.eye(3) - np.outer(r_i, r_i))

        self.I = I + self.I_body

        # Update rotor positions relative to CoM
        self.r_pos_rel = self.r_pos - self.CoM

    def rotation_matrix(self, phi, theta, psi):
        cphi = np.cos(phi); sphi = np.sin(phi)
        cth = np.cos(theta); sth = np.sin(theta)
        cpsi = np.cos(psi); spsi = np.sin(psi)

        R = np.array([
            [cth*cpsi, sphi*sth*cpsi - cphi*spsi, cphi*sth*cpsi + sphi*spsi],
            [cth*spsi, sphi*sth*spsi + cphi*cpsi, cphi*sth*spsi - sphi*cpsi],
            [-sth,     sphi*cth,                  cphi*cth]
        ])
        return R

    def W_matrix(self, phi, theta):
        cphi = np.cos(phi); sphi = np.sin(phi)
        cth = np.cos(theta); tth = np.tan(theta)
        W = np.array([
            [1, sphi*tth, cphi*tth],
            [0, cphi,    -sphi],
            [0, sphi/cth, cphi/cth]
        ])
        return W

    def dynamics(self, t, x, omega):
        # Unpack state
        p = x[0:3]
        v = x[3:6]
        phi, theta, psi = x[6:9]
        omega_body = x[9:12]

        # Rotation matrix body->inertial
        R = self.rotation_matrix(phi, theta, psi)
        W = self.W_matrix(phi, theta)

        # Forces and torques from rotors
        F_i = self.kf * omega**2
        tau_psi_i = self.rotor_dirs * self.km * omega**2

        # Total thrust force in body frame
        F_total = np.array([0,0,np.sum(F_i)])

        # Total torque
        tau_total = np.zeros(3)
        for i in range(4):
            r_i = self.r_pos_rel[i]
            F_vec = np.array([0, 0, F_i[i]])
            tau_total += np.cross(r_i, F_vec) + np.array([0, 0, tau_psi_i[i]])

        # Aerodynamic drag forces
        F_drag = -self.Cd @ v
        tau_drag = -self.Ctau @ omega_body

        # Translational acceleration
        a = (1/self.m) * (self.m * np.array([0,0,-9.81]) + R @ F_total + F_drag)

        # Rotational acceleration
        omega_dot = np.linalg.inv(self.I) @ (tau_total - np.cross(omega_body, self.I @ omega_body) + tau_drag)

        # Euler angle rates
        eta_dot = W @ omega_body

        dxdt = np.zeros_like(x)
        dxdt[0:3] = v
        dxdt[3:6] = a
        dxdt[6:9] = eta_dot
        dxdt[9:12] = omega_dot

        return dxdt

    def simulate(self, omega_func, x0, t_span, t_eval):
        """
        omega_func: function omega(t, x) -> rotor speeds array (4,)
        x0: initial state vector (12,)
        t_span: (t0, tf)
        t_eval: times at which to store results
        """
        def fun(t, x):
            omega = omega_func(t, x)
            return self.dynamics(t, x, omega)

        sol = solve_ivp(fun, t_span, x0, t_eval=t_eval)
        return sol
