    
class Move:
    def moving (self,t, start_frame_pos,end_frame_pos, pos):
        """"
        Moving Function from known start and end positions (used for sitting, lying, etc...)
        """
        
        theta_spot_updated = pos[12]
        x_spot_updated =  pos[13]
        y_spot_updated =  pos[14]
        z_spot_updated =  pos[15]
        
    
        #interpolate new frame position 
        frame_pos = np.zeros(6)
        
        for i in range (0,6):
            frame_pos[i] = start_frame_pos[i]  + (end_frame_pos[i]- start_frame_pos[i])*t
        
        theta_spot_updated [3] = frame_pos[0]
        theta_spot_updated [4] = frame_pos[1]
        theta_spot_updated [5] = frame_pos[2]
        #rotation matrix for frame position
        Mf = Spot.xyz_rotation_matrix (self,frame_pos[0],frame_pos[1],frame_pos[2],False)
        
        #rotation matrix for spot position (only around z axis)
        Ms = Spot.xyz_rotation_matrix (self,0,0,theta_spot_updated[2],False)
        
        # frame corners position coordinaterelative to frame center
        x_frame = [Spot.xlf, Spot.xrf, Spot.xrr, Spot.xlr]
        y_frame = [Spot.ylf, Spot.yrf, Spot.yrr, Spot.ylr]
        z_frame = [0,0,0,0]
        
        #New absolute frame center position
        frame_center_abs = Spot.new_coordinates(self,Ms,frame_pos[3],frame_pos[4],frame_pos[5],x_spot_updated[0],y_spot_updated[0],z_spot_updated[0])
   
        #absolute frame corners position coordinates  
        x_frame_corner_abs = np.zeros(4)
        y_frame_corner_abs = np.zeros(4)
        z_frame_corner_abs = np.zeros(4)
                    
        for i in range (0,4):
            frame_corner = Spot.new_coordinates(self,Mf,x_frame[i],y_frame[i],z_frame[i],0,0,0)
            frame_corner_abs = Spot.new_coordinates(self,Ms,frame_corner[0],frame_corner[1],frame_corner[2],frame_center_abs[0],frame_center_abs[1],frame_center_abs[2])
            x_frame_corner_abs[i] = frame_corner_abs[0]
            y_frame_corner_abs[i] = frame_corner_abs[1]
            z_frame_corner_abs[i] = frame_corner_abs[2]
        
        #calculate current relative position
        xleg = np.zeros(4)
        yleg = np.zeros(4)
        zleg = np.zeros(4)
               
        
        #Leg relative position to front corners
        Mi = Spot.xyz_rotation_matrix(self,-theta_spot_updated[3],-theta_spot_updated[4],-(theta_spot_updated[2]+theta_spot_updated[5]),True)   

        for i in range (0,4):                        
            leg = Spot.new_coordinates(self,Mi,x_spot_updated[i+2]-x_frame_corner_abs[i],y_spot_updated[i+2]-y_frame_corner_abs[i],z_spot_updated[i+2]-z_frame_corner_abs[i],0,0,0)
            xleg[i] = leg[0]
            yleg[i] = leg[1]
            zleg[i] = leg[2]
        
        
        x_spot_updated[1] = frame_center_abs [0]     
        y_spot_updated[1] = frame_center_abs [1]          
        z_spot_updated[1] = frame_center_abs [2]    

                
        pos = [xleg[0],yleg[0],zleg[0],xleg[1],yleg[1],zleg[1],xleg[2],yleg[2],zleg[2],xleg[3],yleg[3],zleg[3],theta_spot_updated,x_spot_updated,y_spot_updated,z_spot_updated]    
        return pos