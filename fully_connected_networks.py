"""
Implements fully connected networks in PyTorch.
WARNING: you SHOULD NOT use ".to()" or ".cuda()" in each implementation block.
"""
import torch
import libs
from libs import Solver


class Linear(object):

    @staticmethod
    def forward(x, w, b):
        """
        Computes the forward pass for an linear (fully-connected) layer.
        The input x has shape (N, d_1, ..., d_k) and contains a minibatch of N
        examples, where each example x[i] has shape (d_1, ..., d_k). We will
        reshape each input into a vector of dimension D = d_1 * ... * d_k, and
        then transform it to an output vector of dimension M.
        Inputs:
        - x: A tensor containing input data, of shape (N, d_1, ..., d_k)
        - w: A tensor of weights, of shape (D, M)
        - b: A tensor of biases, of shape (M,)
        Returns a tuple of:
        - out: output, of shape (N, M)
        - cache: (x, w, b)
        """
        out = None
        N = x.size(dim=0)  
        D = torch.prod(torch.tensor(x.shape[1:])).item()  
        out = torch.mm(x.reshape(N,D), w) + b 
        cache = (x, w, b)
        return out, cache

    @staticmethod
    def backward(dout, cache):
        """
        Computes the backward pass for an linear layer.
        Inputs:
        - dout: Upstream derivative, of shape (N, M)
        - cache: Tuple of:
          - x: Input data, of shape (N, d_1, ... d_k)
          - w: Weights, of shape (D, M)
          - b: Biases, of shape (M,)
        Returns a tuple of:
        - dx: Gradient with respect to x, of shape
          (N, d1, ..., d_k)
        - dw: Gradient with respect to w, of shape (D, M)
        - db: Gradient with respect to b, of shape (M,)
        """
        x, w, b = cache
        dx, dw, db = None, None, None
        N = x.size(dim=0)  
        D = torch.prod(torch.tensor(x.shape[1:])).item() 
        dx = torch.mm(dout, w.t()) 
        dx = dx.reshape(x.size())  
        dw = torch.mm(x.reshape(N,D).t(), dout)  
        db = torch.sum(dout, dim=0)  
        return dx, dw, db


class ReLU(object):

    @staticmethod
    def forward(x):
        """
        Computes the forward pass for a layer of rectified
        linear units (ReLUs).
        Input:
        - x: Input; a tensor of any shape
        Returns a tuple of:
        - out: Output, a tensor of the same shape as x
        - cache: x
        """
        out = None
        out = torch.max(x,torch.zeros_like(x))
        # به ازای مقادیر منفی در اینجا صفر میگذاریم و به ازای مقادیر مثبت خودشان را میگذاریم که همانند کاریست که ReLU انجام میدهد. 
        cache = x
        return out, cache

    @staticmethod
    def backward(dout, cache):
        """
        Computes the backward pass for a layer of rectified
        linear units (ReLUs).
        Input:
        - dout: Upstream derivatives, of any shape
        - cache: Input x, of same shape as dout
        Returns:
        - dx: Gradient with respect to x
        """
        dx, x = None, cache
# مشتق برابر یک است در جاهایی که ورودی بزرگتر از 0 است.
        dx = dout * (cache > 0) 
        return dx


class Linear_ReLU(object):

    @staticmethod
    def forward(x, w, b):
        """
        Convenience layer that performs an linear transform
        followed by a ReLU.

        (x, w, b)
        Inputs:
        - x: Input to the linear layer
        - w, b: Weights for the linear layer
        Returns a tuple of:
        - out: Output from the ReLU
        - cache: Object to give to the backward pass (hint: cache = (fc_cache, relu_cache))
        """
        out = None
        cache = None
        N1 = x.size(dim=0) 
        D1 = torch.prod(torch.tensor(x.shape[1:])).item()  
        out_linear = torch.mm(x.reshape(N1,D1), w) + b 
        out = torch.max(out_linear,torch.zeros_like(out_linear))
        cache = (x,w,b,out_linear)
        return out, cache

    @staticmethod
    def backward(dout, cache):
        """
        dx = torch.mm(dout, w.t())  # Gradient with respect to the reshaped input
        dx = dx.reshape(x.size())  # Reshape the gradient with respect to the input
        dw = torch.mm(x.reshape(N,D).t(), dout)  # Gradient with respect to the weights
        db = torch.sum(dout, dim=0)
        Backward pass for the linear-relu convenience layer
        """
        dx, dw, db = None, None, None
        x,w,b,out_linear = cache
        N = x.size(dim=0) 
        D = torch.prod(torch.tensor(x.shape[1:])).item() 
        d_relu = dout * (out_linear > 0) 
        dx = torch.mm(d_relu, w.t())
        dx = dx.reshape(x.size())
        dw = torch.mm(x.reshape(N,D).t(), d_relu)
        db = torch.sum(d_relu, dim=0)
        return dx, dw, db


def softmax_loss(x, y):
    """
    Computes the loss and gradient for softmax classification.
    Inputs:
    - x: Input data, of shape (N, C) where x[i, j] is the score for
      the jth class for the ith input.
    - y: Vector of labels, of shape (N,) where y[i] is the label
      for x[i] and 0 <= y[i] < C
    Returns a tuple of:
    - loss: Scalar giving the loss
    - dx: Gradient of the loss with respect to x
    expe_scores
    """
    loss = None
    dx = None
    # اینجا خروجی نسبت به ورودی که ما دادیم تولید میشود.این خروجی نسبت به مجموع احتمال کلاس ها نرمالزه شده است و بین 0و1 قرار میگیرد. . 
    f = torch.exp(x)/ torch.sum(torch.exp(x), axis=1, keepdims=True)
    N = x.size(dim=0)
    # در اینجا با اندیس کلاس درست، احتمال های سافتمکس محاسبه میشود . بر روی آنها میانگین گیری انجام میشود تا مشخص شود که نمرات هر کلاس چه قدر با برچسب واقعی مشابهت دارند. 
    loss = -torch.sum(torch.log(f[torch.arange(N),y])) / N
    dx =f  
    # با قاعده ی زنجیره ای مشتق حساب می شود. 
    dx[torch.arange(N),y] -= 1  
    dx /= N 
    return loss, dx


class TwoLayerNet(object):
    """
    A two-layer fully-connected neural network with ReLU nonlinearity and
    softmax loss that uses a modular layer design. We assume an input dimension
    of D, a hidden dimension of H, and perform classification over C classes.
    The architecure should be linear - relu - linear - softmax.
    Note that this class does not implement gradient descent; instead, it
    will interact with a separate Solver object that is responsible for running
    optimization.

    The learnable parameters of the model are stored in the dictionary
    self.params that maps parameter names to PyTorch tensors.
    """

    def __init__(self, input_dim=3*32*32, hidden_dim=100, num_classes=10,
                 weight_scale=1e-3, reg=0.0,
                 dtype=torch.float32, device='cpu'):
        """
        Initialize a new network.
        Inputs:
        - input_dim: An integer giving the size of the input
        - hidden_dim: An integer giving the size of the hidden layer
        - num_classes: An integer giving the number of classes to classify
        - weight_scale: Scalar giving the standard deviation for random
          initialization of the weights.
        - reg: Scalar giving L2 regularization strength.
        - dtype: A torch data type object; all computations will be
          performed using this datatype. float is faster but less accurate,
          so you should use double for numeric gradient checking.
        - device: device to use for computation. 'cpu' or 'cuda'
        """
        self.params = {}
        self.reg = reg
        
        self.params['W1'] = weight_scale * torch.randn(input_dim, hidden_dim,device=device, dtype=dtype )
        self.params['b1'] = torch.zeros(hidden_dim,device=device, dtype=dtype )
        self.params['W2'] = weight_scale * torch.randn(hidden_dim, num_classes,device=device, dtype=dtype )
        self.params['b2'] = torch.zeros(num_classes,device=device, dtype=dtype )
    

    def save(self, path):
        checkpoint = {
          'reg': self.reg,
          'params': self.params,
        }

        torch.save(checkpoint, path)
        print("Saved in {}".format(path))

    def load(self, path, dtype, device):
        checkpoint = torch.load(path, map_location='cpu')
        self.params = checkpoint['params']
        self.reg = checkpoint['reg']
        for p in self.params:
            self.params[p] = self.params[p].type(dtype).to(device)
        print("load checkpoint file: {}".format(path))

    def loss(self, X, y=None):
        """
        Compute loss and gradient for a minibatch of data.

        Inputs:
        - X: Tensor of input data of shape (N, d_1, ..., d_k)
        - y: int64 Tensor of labels, of shape (N,). y[i] gives the
          label for X[i].
        
        Returns:
        If y is None, then run a test-time forward pass of the model
        and return:
        - scores: Tensor of shape (N, C) giving classification scores,
          where scores[i, c] is the classification score for X[i]
          and class c.
        If y is not None, then run a training-time forward and backward
        pass and return a tuple of:
        - loss: Scalar value giving the loss
        - grads: Dictionary with the same keys as self.params, mapping
          parameter names to gradients of the loss with respect to
          those parameters.
        """
        scores = None
         
        Lrelu_out1 , cache1 = Linear_ReLU.forward(X,self.params['W1'],self.params['b1'])
        x1,self.params['W1'],self.params['b1'],out_linear1 = cache1
        linear_out2 , cache2 = Linear.forward(Lrelu_out1,self.params['W2'],self.params['b2'])
        x2,self.params['W2'],self.params['b2'] = cache2
        # در اینجا نمرات مثل خروجی لایه ی سافتمکس تعیین میشوند که برای حالت تست خواهد بود که وارد فاز آموزش نشویم و گرادیان ها را آپدیت نکنیم. . 
        scores = torch.exp(linear_out2)/ torch.sum(torch.exp(linear_out2), axis=1, keepdims=True)
        

        
        if y is None:
            return scores
        
        loss, grads = 0, {}
        loss,ds = softmax_loss(linear_out2,y)
        loss += self.reg * (torch.sum(self.params['W1'] * self.params['W1']) + torch.sum(self.params['W2'] * self.params['W2'])) 
        dLrelu_out1,dw2,db2 = Linear.backward(ds,cache2)
        dx,dw1,db1 = Linear_ReLU.backward(dLrelu_out1,cache1)
        grads['W1'] = dw1
        grads['W2'] = dw2
        grads['b1'] = db1
        grads['b2'] = db2

        return loss, grads
        
        
      
class FullyConnectedNet(object):
    """
    A fully-connected neural network with an arbitrary number of hidden layers,
    ReLU nonlinearities, and a softmax loss function.
    For a network with L layers, the architecture will be:

    {linear - relu - [dropout]} x (L - 1) - linear - softmax

    where dropout is optional, and the {...} block is repeated L - 1 times.

    Similar to the TwoLayerNet above, learnable parameters are stored in the
    self.params dictionary and will be learned using the Solver class.
    """

    def __init__(self, hidden_dims, input_dim=3*32*32, num_classes=10,
                 dropout=0.0, reg=0.0, weight_scale=1e-2, seed=None,
                 dtype=torch.float, device='cpu'):
        """
        Initialize a new FullyConnectedNet.

        Inputs:
        - hidden_dims: A list of integers giving the size of each
          hidden layer.
        - input_dim: An integer giving the size of the input.
        - num_classes: An integer giving the number of classes to classify.
        - dropout: Scalar between 0 and 1 giving the drop probability
          for networks with dropout. If dropout=0 then the network
          should not use dropout.
        - reg: Scalar giving L2 regularization strength.
        - weight_scale: Scalar giving the standard deviation for random
          initialization of the weights.
        - seed: If not None, then pass this random seed to the dropout
          layers. This will make the dropout layers deteriminstic so we
          can gradient check the model.
        - dtype: A torch data type object; all computations will be
          performed using this datatype. float is faster but less accurate,
          so you should use double for numeric gradient checking.
        - device: device to use for computation. 'cpu' or 'cuda'
        """
        self.use_dropout = dropout != 0
        self.reg = reg
        self.num_layers = 1 + len(hidden_dims)
        self.dtype = dtype
        self.params = {}
        
        for i in range(1,self.num_layers-1):
            self.params['W' + str(i+1)] = weight_scale * torch.randn(hidden_dims[i-1], hidden_dims[i] ,device=device, dtype=dtype ) 
            self.params['b' + str(i+1)] = torch.zeros(hidden_dims[i],device=device, dtype=dtype)
        self.params['W1'] = weight_scale * torch.randn(input_dim, hidden_dims[0],device=device, dtype=dtype )
        self.params['b1'] = torch.zeros(hidden_dims[0],device=device, dtype=dtype)
        self.params['W' + str(self.num_layers)] = weight_scale * torch.randn(hidden_dims[self.num_layers-2],num_classes,device=device,dtype=dtype )
        self.params['b' + str(self.num_layers)] = torch.zeros(num_classes,device=device, dtype=dtype)
        # When using dropout we need to pass a dropout_param dictionary
        # to each dropout layer so that the layer knows the dropout
        # probability and the mode (train / test). You can pass the same
        # dropout_param to each dropout layer.
        self.dropout_param = {}
        if self.use_dropout:
            self.dropout_param = {'mode': 'train', 'p': dropout}
            if seed is not None:
                self.dropout_param['seed'] = seed

    def save(self, path):
        checkpoint = {
          'reg': self.reg,
          'dtype': self.dtype,
          'params': self.params,
          'num_layers': self.num_layers,
          'use_dropout': self.use_dropout,
          'dropout_param': self.dropout_param,
        }

        torch.save(checkpoint, path)
        print("Saved in {}".format(path))

    def load(self, path, dtype, device):
        checkpoint = torch.load(path, map_location='cpu')
        self.params = checkpoint['params']
        self.dtype = dtype
        self.reg = checkpoint['reg']
        self.num_layers = checkpoint['num_layers']
        self.use_dropout = checkpoint['use_dropout']
        self.dropout_param = checkpoint['dropout_param']

        for p in self.params:
            self.params[p] = self.params[p].type(dtype).to(device)

        print("load checkpoint file: {}".format(path))

    def loss(self, X, y=None):
        """
        Compute loss and gradient for the fully-connected net.
        Input / output: Same as TwoLayerNet above.
        """
        X = X.to(self.dtype)
        mode = 'test' if y is None else 'train'

        # Set train/test mode for batchnorm params and dropout param
        # since they behave differently during training and testing.
        if self.use_dropout:
            self.dropout_param['mode'] = mode
        scores = None
        out = {} # یک لیست برای خروجی های هر لایه تعریف میکنیم که تنسورهای خروجی هر لایه را در خود جا میدهید و با هر لایه جلو میرود
        out[0] = X  # ورودی را به عنوان اولین المنت از لیست خروجی میدهیم تا در حلقه ای که مینویسیم برای لایه ی اول، آرگومان ها درست باشند. 
        cache = {} # این برای عملیات پس انتشار تعریف میشود که هر لایه ی خورجی باید آنرا داشته باشد. 
        cache_drop = {} # این هم برای عملیات پس انتشار برای دراپ اوت تعریف میکنیم که با هر لایه دراپ اوت، عضو جدیدی میگیرد.. 
        for i in range(0,self.num_layers-1):
            out[i+1] , cache[i+1] = Linear_ReLU.forward(out[i],self.params['W'+ str(i+1)],self.params['b'+ str(i+1)])
            if self.use_dropout:
                out[i+1] , cache_drop[i+1] = Dropout.forward(out[i+1], self.dropout_param)
        scores , cache[self.num_layers] = Linear.forward(out[self.num_layers-1],self.params['W' + str(self.num_layers)],self.params['b'+ str(self.num_layers)])
        if self.use_dropout:
            scores, cache_drop[self.num_layers] = Dropout.forward(scores, self.dropout_param)
        
        # If test mode return early
        if mode == 'test':
            return scores
# با استفاده از کش های هر لایه ی فوروارد ورودی به خروجی و کش های دراپ اوت ها مسیر پس اشنتار را محاسبه میکنیم.
        loss, grads = 0.0, {}
        dout = {}
        loss , ds = softmax_loss(scores,y)
        if self.use_dropout:
                ds = Dropout.backward(ds, cache_drop[self.num_layers])
        dout[self.num_layers], grads['W'+ str(self.num_layers)],grads['b' + str(self.num_layers)] = Linear.backward(ds,cache[self.num_layers]) 
        grads['W'+ str(self.num_layers)] = grads['W'+ str(self.num_layers)] + self.reg * grads['W'+ str(self.num_layers)]               
        for i in range (self.num_layers-1,1,-1):
            if self.use_dropout:
                dout[i+1] = Dropout.backward(dout[i+1], cache_drop[i])
            dout[i],grads['W'+str(i)],grads['b' + str(i)] = Linear_ReLU.backward(dout[i+1],cache[i])
            grads['W'+ str(i)] = grads['W'+ str(i)] + self.reg * grads['W'+ str(i)]
            loss += 0.5 * self.reg * torch.sum(self.params['W' + str(i+1)] * self.params['W' + str(i+1)])
        if self.use_dropout:
            dout[2] = Dropout.backward(dout[2], cache_drop[1])
        dx,grads['W1'],grads['b1'] = Linear_ReLU.backward(dout[2],cache[1])
        loss += 0.5 * self.reg * torch.sum(self.params['W1'] * self.params['W1'])
        return loss, grads  
        

def create_solver_instance(data_dict, dtype, device):
    model = TwoLayerNet(hidden_dim=200, dtype=dtype, device=device)
    #############################################################
    # TODO: Use a Solver instance to train a TwoLayerNet that    #
    # achieves at least 50% accuracy on the validation set.      #
    #############################################################
    import libs
    from libs import Solver
    update_rule = libs.Solver.sgd
    optim_config = {'learning_rate': 0.05}
    lr_decay = 0.99
    num_epochs = 30
    batch_size = 100
    print_every = 400
    print_acc_every = 10
    verbose = True
    num_train_samples = None
    num_val_samples = None
    checkpoint_name = None
    
    # Create the Solver instance
    solver = libs.Solver(model, data_dict,
                               update_rule=update_rule,
                               optim_config=optim_config,
                               lr_decay=lr_decay,
                               num_epochs=num_epochs,
                               batch_size=batch_size,
                               print_every=print_every,
                               print_acc_every=print_acc_every,
                               verbose=verbose,
                               num_train_samples=num_train_samples,
                               num_val_samples=num_val_samples,
                               checkpoint_name=checkpoint_name,
                               device=device)
    
    #solver.train()
    

    return solver


def get_three_layer_network_params():
    ###############################################################
    # TODO: Change weight_scale and learning_rate so your         #
    # model achieves 100% training accuracy within 20 epochs.     #
    ###############################################################
    weight_scale = 0.1  # Experiment with this!
    learning_rate = 0.08  # Experiment with this!
    ################################################################
    #                             END OF YOUR CODE                 #
    ################################################################
    return weight_scale, learning_rate


def get_five_layer_network_params():
    ################################################################
    # TODO: Change weight_scale and learning_rate so your          #
    # model achieves 100% training accuracy within 20 epochs.      #
    ################################################################
    learning_rate = 0.08  # Experiment with this!
    weight_scale = 0.1   # Experiment with this!
    ################################################################
    #                       END OF YOUR CODE                       #
    ################################################################
    return weight_scale, learning_rate


def sgd(w, dw, config=None):
    """
    Performs vanilla stochastic gradient descent.
    config format:
    - learning_rate: Scalar learning rate.
    """
    if config is None:
        config = {}
    config.setdefault('learning_rate', 1e-2)

    w -= config['learning_rate'] * dw
    return w, config


def sgd_momentum(w, dw, config=None):
    """
    Performs stochastic gradient descent with momentum.
    config format:
    - learning_rate: Scalar learning rate.
    - momentum: Scalar between 0 and 1 giving the momentum value.
      Setting momentum = 0 reduces to sgd.
    - velocity: A numpy array of the same shape as w and dw used to
      store a moving average of the gradients.
    """
    if config is None:
        config = {}
    config.setdefault('learning_rate', 1e-2)
    config.setdefault('momentum', 0.9)
    v = config.get('velocity', torch.zeros_like(w))

    next_w = None
    learning_rate = config['learning_rate']
    momentum = config['momentum']
    v = momentum * v - learning_rate * dw
    config['velocity'] = v
    next_w = w + v

    return next_w, config


def rmsprop(w, dw, config=None):
    """
    Uses the RMSProp update rule, which uses a moving average of squared
    gradient values to set adaptive per-parameter learning rates.
    config format:
    - learning_rate: Scalar learning rate.
    - decay_rate: Scalar between 0 and 1 giving the decay rate for the squared
      gradient cache.
    - epsilon: Small scalar used for smoothing to avoid dividing by zero.
    - cache: Moving average of second moments of gradients.
    """
    if config is None:
        config = {}
    config.setdefault('learning_rate', 1e-2)
    config.setdefault('decay_rate', 0.99)
    config.setdefault('epsilon', 1e-8)
    config.setdefault('cache', torch.zeros_like(w))
    
    next_w = None
    learning_rate = config['learning_rate']
    decay_rate = config['decay_rate']
    epsilon = config['epsilon']
    cache = config['cache']
    cache = decay_rate * cache + (1 - decay_rate) * (dw * dw)
    config['cache'] = cache
    next_w = w - learning_rate * (dw / (torch.sqrt(cache) + epsilon))



    return next_w, config


def adam(w, dw, config=None):
    """
    Uses the Adam update rule, which incorporates moving averages of both the
    gradient and its square and a bias correction term.
    config format:
    - learning_rate: Scalar learning rate.
    - beta1: Decay rate for moving average of first moment of gradient.
    - beta2: Decay rate for moving average of second moment of gradient.
    - epsilon: Small scalar used for smoothing to avoid dividing by zero.
    - m: Moving average of gradient.
    - v: Moving average of squared gradient.
    - t: Iteration number.
    """
    if config is None:
        config = {}
    config.setdefault('learning_rate', 1e-3)
    config.setdefault('beta1', 0.9)
    config.setdefault('beta2', 0.999)
    config.setdefault('epsilon', 1e-8)
    config.setdefault('m', torch.zeros_like(w))
    config.setdefault('v', torch.zeros_like(w))
    config.setdefault('t', 0)

    next_w = None
    learning_rate = config['learning_rate']
    beta1 = config['beta1']
    beta2 = config['beta2']
    epsilon = config['epsilon']
    m = config['m']
    v = config['v']
    t = config['t']
    t = t + 1
    config['t'] = t
    m = beta1 * m + (1 - beta1) * dw
    mh = m / (1 - beta1 ** t)
    config['m'] = m
    v = beta2 * v + (1 - beta2) * (dw ** 2)
    vh = v / (1 - beta2 ** t)
    config['v'] = v
    next_w = w - learning_rate * (mh / (torch.sqrt(vh) + epsilon))
    

    return next_w, config
 

class Dropout(object):

    @staticmethod
    def forward(x, dropout_param):
        """
        Performs the forward pass for (inverted) dropout.
        Inputs:
        - x: Input data: tensor of any shape
        - dropout_param: A dictionary with the following keys:
          - p: Dropout parameter. We *drop* each neuron output with
            probability p.
          - mode: 'test' or 'train'. If the mode is train, then
            perform dropout;
          if the mode is test, then just return the input.
          - seed: Seed for the random number generator. Passing seed
            makes this
            function deterministic, which is needed for gradient checking
            but not in real networks.
        Outputs:
        - out: Tensor of the same shape as x.
        - cache: tuple (dropout_param, mask). In training mode, mask
          is the dropout mask that was used to multiply the input; in
        NOTE: Please implement **inverted** dropout, not the vanilla
              version of dropout.
        See http://cs231n.github.io/neural-networks-2/#reg for more details.
        NOTE 2: Keep in mind that p is the probability of **dropping**
                a neuron output; this might be contrary to some sources,
                where it is referred to as the probability of keeping a
                neuron output.
        """
        p, mode = dropout_param['p'], dropout_param['mode']
        if 'seed' in dropout_param:
            torch.manual_seed(dropout_param['seed'])

        mask = None
        out = None
        p = 1 - p
        if mode == 'train':
             random = torch.rand_like(x)
             mask = (random < p)/p
             out = mask * x
        elif mode =='test':
             out = x
        cache = (dropout_param, mask)

        return out, cache

    @staticmethod
    def backward(dout, cache):
        """
        Perform the backward pass for (inverted) dropout.
        Inputs:
        - dout: Upstream derivatives, of any shape
        - cache: (dropout_param, mask) from Dropout.forward.
        """
        dropout_param, mask = cache
        mode = dropout_param['mode']

        dx = None
        if mode == 'train':
            dx = dout * mask
        elif mode == 'test':
            dx = dout
        return dx

