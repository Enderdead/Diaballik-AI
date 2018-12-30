import tensorflow as tf 
import numpy as np 
from pickle import dumps, load
from threading import Lock

# Amélioration  , connecté les positions

class DeepNeuronalNetwork():
    def __init__(self):
        ######## UN SEUL BATCH
        init_kernels = tf.random_normal_initializer()
        # Board + move  ||| board first after pos
        self.tf_input = tf.placeholder(tf.float32, shape=(None, 7, 7, 4))
        # Board
        self.tf_inputBoard = self.tf_input[0:1,:,:,0:2]
        
        self.input_lock = Lock()

        with tf.name_scope("A_main"):
            self.tf_kernel_A = tf.Variable(init_kernels([4,4,4,8]),dtype=tf.float32,name="kernel_A")
            self.tf_convolution_A = tf.nn.conv2d(self.tf_input, self.tf_kernel_A, strides=[1,3,3,1], padding="VALID")
            self.tf_bias_A = tf.Variable(np.zeros((2,2,8),dtype=np.float),dtype=tf.float32,name="bias_A")
            self.tf_A = tf.nn.tanh(self.tf_convolution_A+self.tf_bias_A)


        with tf.name_scope("B_main"):
            self.tf_kernel_B = tf.Variable(init_kernels([3,3,4,8]),dtype=tf.float32,name="kernel_B")
            self.tf_convolution_B = tf.nn.conv2d(self.tf_input, self.tf_kernel_B, strides=[1,2,2,1], padding="VALID")
            self.tf_bias_B = tf.Variable(np.zeros((3,3,8),dtype=np.float32),name="bias_B")
            self.tf_B = tf.nn.tanh(self.tf_convolution_B+self.tf_bias_B)

        with tf.name_scope("C_main"):
            self.tf_kernel_C = tf.Variable(init_kernels([2,2,8,8]),dtype=tf.float32,name="kernel_C")
            self.tf_convolution_C = tf.nn.conv2d(self.tf_B, self.tf_kernel_C, strides=[1,1,1,1], padding="VALID")
            self.tf_bias_C = tf.Variable(np.zeros((2,2,8),dtype=np.float32),name="bias_C")
            self.tf_C = tf.nn.tanh(self.tf_convolution_C+self.tf_bias_C)

        with tf.name_scope("D_main"):
            self.tf_D_input = tf.concat([self.tf_A,self.tf_C], 3)
            self.tf_kernel_D = tf.Variable(init_kernels([2,2,16,16]),dtype=tf.float32,name="kernel_D")
            self.tf_convolution_D = tf.nn.conv2d(self.tf_D_input, self.tf_kernel_D, strides=[1,1,1,1], padding="VALID")
            self.tf_bias_D = tf.Variable(np.zeros((1,1,16),dtype=np.float32),name="bias_D")
            self.tf_D = tf.nn.tanh(self.tf_convolution_D+self.tf_bias_D)

        with tf.name_scope("E_main"):
            self.tf_E_input = tf.squeeze(self.tf_D,[1,2])
            self.tf_kernel_E = tf.Variable(init_kernels([16,5]), dtype=tf.float32,name="kernel_E")
            self.tf_bias_E = tf.Variable(tf.zeros([5],dtype=tf.float32),dtype=tf.float32,name="bias_E")
            self.tf_E = tf.nn.tanh(tf.matmul(self.tf_E_input, self.tf_kernel_E) + self.tf_bias_E)

        with tf.name_scope("F_main"):
            self.tf_kernel_F = tf.Variable(init_kernels([5,1]), dtype=tf.float32,name="kernel_F")
            self.tf_F = tf.matmul(self.tf_E,self.tf_kernel_F)


        with tf.name_scope("A_aux"):
            self.tf_kernel_A_aux = tf.Variable(init_kernels([4,4,2,4]),dtype=tf.float32,name="kernel_A_aux")
            self.tf_convolution_A_aux = tf.nn.conv2d(self.tf_inputBoard, self.tf_kernel_A_aux, strides=[1,3,3,1], padding="VALID")
            self.tf_bias_A_aux = tf.Variable(np.zeros((2,2,4),dtype=np.float32),name="bias_A_aux")
            self.tf_A_aux = tf.nn.tanh(self.tf_convolution_A_aux+self.tf_bias_A_aux)


        with tf.name_scope("B_aux"):
            self.tf_kernel_B_aux = tf.Variable(init_kernels([3,3,2,4]),dtype=tf.float32,name="kernel_B_aux")
            self.tf_convolution_B_aux = tf.nn.conv2d(self.tf_inputBoard, self.tf_kernel_B_aux, strides=[1,2,2,1], padding="VALID")
            self.tf_bias_B_aux = tf.Variable(np.zeros((3,3,4),dtype=np.float32),name="bias_B_aux")
            self.tf_B_aux = tf.nn.tanh(self.tf_convolution_B_aux+self.tf_bias_B_aux)

        with tf.name_scope("C_main"):
            self.tf_kernel_C_aux = tf.Variable(init_kernels([2,2,4,4]),dtype=tf.float32,name="kernel_C_aux")
            self.tf_convolution_C_aux = tf.nn.conv2d(self.tf_B_aux, self.tf_kernel_C_aux, strides=[1,1,1,1], padding="VALID")
            self.tf_bias_C_aux = tf.Variable(np.zeros((2,2,4),dtype=np.float32),name="bias_C_aux")
            self.tf_C_aux = tf.nn.tanh(self.tf_convolution_C_aux+self.tf_bias_C_aux)

        with tf.name_scope("D_aux"):
            self.tf_D_input_aux = tf.concat([self.tf_A_aux,self.tf_C_aux], 3)
            self.tf_kernel_D_aux = tf.Variable(init_kernels([2,2,8,8]),dtype=tf.float32,name="kernel_D_aux")
            self.tf_convolution_D_aux = tf.nn.conv2d(self.tf_D_input_aux, self.tf_kernel_D_aux, strides=[1,1,1,1], padding="VALID")
            self.tf_bias_D_aux = tf.Variable(np.zeros((1,1,8),dtype=np.float32),name="bias_D_aux")
            self.tf_D_aux = tf.nn.tanh(self.tf_convolution_D_aux+self.tf_bias_D_aux)

        with tf.name_scope("E_aux"):
            self.tf_E_input_aux = tf.squeeze(self.tf_D_aux,[1,2])
            self.tf_kernel_E_aux = tf.Variable(init_kernels([8,1]), dtype=tf.float32,name="kernel_E_aux")
            self.tf_bias_E_aux = tf.Variable(tf.zeros([5],dtype=tf.float32),dtype=tf.float32,name="bias_E_aux")
            self.tf_E_aux = tf.nn.tanh(tf.matmul(self.tf_E_input_aux, self.tf_kernel_E_aux) + self.tf_bias_E_aux)

        with tf.name_scope("output"):
            # Proba pour chaque move
            self.tf_output_pos = tf.nn.softmax(tf.reshape(self.tf_F,[1,-1]))
            # Proba pour la win
            self.tf_output_win = self.tf_E_aux

        with tf.name_scope("label"):
            # De cette forme [[1]]
            self.tf_winner = tf.placeholder(tf.float32, (1,1))
            #  De cette forme [0,0,0,1,0,0]
            self.tf_selected_play = tf.placeholder(tf.float32, (1,None))

        with tf.name_scope("losss"):
            self.tf_loss = tf.reduce_mean(tf.square(self.tf_winner-self.tf_output_win)) - tf.reduce_mean(self.tf_selected_play*tf.log(self.tf_output_pos))

        with tf.name_scope("train"):
            self.tf_coef = tf.placeholder(tf.float32, shape=())
            self.tf_optimizer = tf.train.AdamOptimizer(learning_rate=self.tf_coef*0.001)
            self.tf_train_op = self.tf_optimizer.minimize(self.tf_loss)


        with tf.name_scope("save"):
            self.saved_param = [self.tf_kernel_A, self.tf_bias_A,\
                           self.tf_kernel_B, self.tf_bias_B,\
                           self.tf_kernel_C, self.tf_bias_C,\
                           self.tf_kernel_D, self.tf_bias_D,\
                           self.tf_kernel_E, self.tf_bias_E,\
                           self.tf_kernel_F,\
                           self.tf_kernel_A_aux, self.tf_bias_A_aux,\
                           self.tf_kernel_B_aux, self.tf_bias_B_aux,\
                           self.tf_kernel_C_aux, self.tf_bias_C_aux,\
                           self.tf_kernel_D_aux, self.tf_bias_D_aux,\
                           self.tf_kernel_E_aux, self.tf_bias_E_aux,]

            for param in self.saved_param:
                name = param.name.split("/")[-1][:-2]
                self.__setattr__("tf_"+name+"_load", tf.placeholder(tf.float32, param.shape ))

            assing_op = []
            for param in self.saved_param:
                name = param.name.split("/")[-1][:-2]
                assing_op.append(param.assign( self.__getattribute__("tf_"+ name +"_load")  ) )
            self.tf_load_param = tf.group(*assing_op)

        self.tf_config = tf.ConfigProto()
        self.tf_config.gpu_options.allow_growth = True
        self.tf_init = tf.global_variables_initializer()

    def start(self):
        self.tf_sess = tf.Session(config=self.tf_config)
        self.tf_sess.run(self.tf_init)

    def fit(self, board, actions, selected_action_index, winner, coef=1):
        self.input_lock.acquire()
        inputs = [ np.dstack([board,action]) for action in actions ]
        
        indexs = np.zeros((1,len(actions)),dtype=np.float32)
        indexs[0][selected_action_index] = 1

        win = np.array([[winner]])

        self.tf_sess.run(self.tf_train_op, feed_dict={self.tf_input: inputs,self.tf_winner: win, self.tf_selected_play: indexs, self.tf_coef: coef})
        self.input_lock.release()


    def eval(self, board, actions_boards):
        stacked_actions = [np.dstack([board,actions_board]) for actions_board in actions_boards]
        inputs = np.stack(stacked_actions,axis=0)
        self.input_lock.acquire()
        res = self.tf_sess.run([self.tf_output_pos, self.tf_output_win],feed_dict={self.tf_input : inputs})
        self.input_lock.release()
        res[1] = res[1][0][0]
        res[0] = res[0][0]
        return res

    def get_kernel(self,dumped=False):
        self.input_lock.acquire()
        elements = list()
        for param in self.saved_param:
            elements.append(param.eval(self.tf_sess))
        self.input_lock.release()
        if not dumped:
            return elements
        return dumps(elements)


    def load_kernel(self, data, dumped=False):
        self.input_lock.acquire()
        if dumped:
            data = loads(data)
        placeholders = list()
        for param in self.saved_param:
            name = param.name.split("/")[-1][:-2]
            placeholders.append(self.__getattribute__("tf_"+name+"_load"))
        self.tf_sess.run(self.tf_load_param,feed_dict=dict(zip(placeholders,data)))
        self.input_lock.release()
        
    def get_score(self, board):
        inputs = np.array([np.dstack([board,np.zeros_like(board)])])
        res = self.tf_sess.run(self.tf_output_win, feed_dict={self.tf_input: inputs})
        return res[0][0]


