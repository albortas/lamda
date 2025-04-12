import numpy as np

from src.motion.GaitController import GaitController

tstep = 0.01
v_amp = 40
stepl = 0.125
seq = [0, 0.5, 0.25, 0.75]

class CrawlGaitController(GaitController):
    def __init__(self, stance_time, swing_time, time_step, contact_phases):
        super().__init__(stance_time, swing_time, time_step, contact_phases)

    def time_cont(self, t, step_phase):
        t1 = t % 1
        stance = [True, True, True, True]
        for i in range(4):
            if t1<=seq[i]:
                stance[i] = True #Leg is on the ground (absolute position value unchanged)
            else:
                if t1<(seq[i]+stepl):
                    stance[i] = False #leg is lifted (absolute position value changes)
                else :
                    stance[i] = True #Leg is on the ground (absolute position value unchanged)
        
        print(stance)
        stance_test = np.sum(stance)
        
        if stance_test == 4: 
            istart = 0
            iend = 0
            #identify transition start and target
            tstart = (int(t1/0.25)*0.25)
            tend = tstart+0.25
            if (tend==1):
                tend = 0
            
            for i in range (0,4):
                if (tstart == seq[i]):
                    istart = i
                if (tend  == seq[i]):
                    iend = i
            #print("istart: ", istart)
            #print("tend: ", tend)
                    
        """ Compensation calculation with theta """
        v_amp_t = v_amp
        ts = 0.25
        if (step_phase == 'start'):
            if (t1< ts):
                kcomp = t1/ts
                v_amp_t = 0
        elif (step_phase == 'stop'):  
            if (t1 > (1-ts)):
                kcomp = (1-t1)/ts
                v_amp_t = 0
        
            #print("kcomp", kcomp)
            #print("v_amp_t", v_amp_t)
                    
                
        lista = []
        for i in range(4):
            if stance[i] == False:
                log= seq[i] + stepl - t1 
                if log > tstep:
                    lista.append(log)
                else:
                    lista.append("swing_else")
            else:
                lista.append("stance")
        print(lista)
        
    def time_disc(self, ticks):
        contact_modes = self.contacts(ticks)
        phase_index = self.phase_index(ticks)
        lista = []
        print(contact_modes)
        for leg_index in range(4):
            contacto_modo = contact_modes[leg_index]
            if contacto_modo == 0:
                if self.subphase_ticks(ticks) < self.swing_ticks - 1:
                    lista.append("swing_if")
                else:
                    lista.append("swing_else")
            else:
                lista.append("stance")
        print(lista)
        
        
                
if __name__ == "__main__":
    t = 0
    step_phase = "start"
    contact_phases = np.array([[0, 1, 1, 1, 1, 1, 1, 1],  # 0: Balanceo Pierna
                               [1, 1, 1, 1, 0, 1, 1, 1],  # 1: Movimiento de postura adelante
                               [1, 1, 0, 1, 1, 1, 1, 1],
                               [1, 1, 1, 1, 1, 1, 0, 1]])
    
    crawl = CrawlGaitController(0.15, 0.10, 0.01, contact_phases)
    ticks = 0
    
    def time_c(t,step_phase):
        while t < 1:
            crawl.time_cont(t, step_phase)
            t += 0.01
            
    def time_d(ticks):
        while ticks < crawl.phase_length:
            crawl.time_disc(ticks)
            ticks += 1
        
    #time_c(t, step_phase)
    time_d(ticks)