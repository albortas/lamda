class GaitController:
    def __init__(self, stance_time, swing_time, time_step, contact_phases):
        self.stance_time = stance_time      #Tiempo apoyo
        self.swing_time = swing_time        #Tiempo balanceo
        self.time_step = time_step          #Tiempo paso
        self.contact_phases = contact_phases  #Fase contacto

    @property
    def stance_ticks(self):  #Numero de ticks(fase de apoyo)
        return int(self.stance_time/self.time_step)

    @property
    def swing_ticks(self):  #Numero de ticks(fase de balaceo)
        return int(self.swing_time/self.time_step)

    @property
    def phase_ticks(self):  #Crea par verificar (fase balance o apoyo)
        temp = []
        for i in range(len(self.contact_phases[0])):
            if 0 in self.contact_phases[:, i]:
                temp.append(self.swing_ticks)
            else:
                temp.append(self.stance_ticks)
        return temp

    @property
    def phase_length(self): #Calcula el ciclo de en ticks
        return sum(self.phase_ticks)

    def phase_index(self, ticks):
        """ Calcular en qué parte del ciclo de marcha debe estar el robot """
        phase_time = ticks % self.phase_length
        phase_sum = 0
        phase_ticks = self.phase_ticks
        for i in range(len(self.contact_phases[0])):
            phase_sum += phase_ticks[i]
            if phase_time < phase_sum:
                return i

    def subphase_ticks(self, ticks):
        """ Calcular el número de ticks (pasos de tiempo)
            desde el inicio de la fase actual. """
        phase_time = ticks % self.phase_length
        phase_sum = 0
        phase_ticks = self.phase_ticks
        for i in range(len(self.contact_phases[0])):
            phase_sum += phase_ticks[i]
            if phase_time < phase_sum:
                subphase_ticks = phase_time - phase_sum + phase_ticks[i]
                return subphase_ticks

    def contacts(self, ticks):
        """ Calcular qué pies deben estar en contacto """
        return self.contact_phases[:, self.phase_index(ticks)]