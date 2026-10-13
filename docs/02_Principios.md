# Módulo 2 — Principios de las redes neuronales

## 2.1 Modelos paramétricos
Un modelo paramétrico es una función con una forma fija cuyo comportamiento depende de unos **parámetros** θ:

$$\hat{y} = f(\mathbf{x};\, \theta)$$

- **x**: entrada (vector de características).
- **θ**: parámetros (en redes neuronales, **pesos** *w* y **sesgo** *b*).
- **ŷ**: salida o predicción.

*Aprender* consiste en encontrar los θ que hacen que ŷ se parezca a la salida deseada *y*. Ejemplo: la recta ŷ = w·x + b tiene dos parámetros; con distintos *w* y *b* obtenemos rectas distintas.

## 2.2 Modelo de McCulloch y Pitts (1943)
Fue la primera neurona artificial. Funciona así:
- Entradas **binarias** xᵢ ∈ {0, 1}.
- La neurona suma sus entradas: g(x) = Σ xᵢ.
- Se **activa** (salida 1) si la suma alcanza un **umbral** θ:

$$y = \begin{cases} 1 & \text{si } \sum_i x_i \ge \theta \\ 0 & \text{en otro caso} \end{cases}$$

- Una entrada **inhibitoria** activa fuerza la salida a 0.

Con distintos umbrales, la misma neurona implementa compuertas lógicas (con *n* entradas):

| Compuerta | Umbral θ |
|---|---|
| AND | n |
| OR | 1 |
| NOT | θ = 0, con la entrada como inhibitoria |

**Limitación:** no tiene pesos ni aprende. El umbral se fija a mano.

## 2.4 El perceptrón (Rosenblatt, 1958)
Generaliza el modelo anterior en tres puntos:
- Las entradas pueden ser **reales**.
- Cada entrada tiene un **peso** wᵢ, y hay un **sesgo** *b* (el umbral pasado al otro lado de la desigualdad: b = −θ).
- **Aprende** los pesos a partir de ejemplos.

$$z = \mathbf{w}\cdot\mathbf{x} + b, \qquad \hat{y} = \text{escalón}(z) = \begin{cases}1 & z \ge 0\\ 0 & z < 0\end{cases}$$

**Interpretación geométrica:** la ecuación **w·x + b = 0** es un hiperplano (en 2D, una recta) que separa el espacio en dos clases. Los pesos definen la orientación de esa recta y el sesgo su desplazamiento.

### Regla de aprendizaje del perceptrón
Para cada ejemplo (x, y):

$$\mathbf{w} \leftarrow \mathbf{w} + \eta\,(y - \hat{y})\,\mathbf{x}, \qquad b \leftarrow b + \eta\,(y - \hat{y})$$

- Si acierta, el error y − ŷ = 0 y no cambia nada.
- Si falla, empuja la recta hacia el lado correcto.
- η es la **tasa de aprendizaje**.

**Teorema de convergencia:** si los datos son **linealmente separables**, el algoritmo encuentra una solución en un número finito de pasos.

### Limitación: XOR
XOR no es linealmente separable: ninguna recta separa los puntos {(0,1), (1,0)} de {(0,0), (1,1)}. Minsky y Papert (1969) lo demostraron, y esto motiva las **redes multicapa** (módulo 4).

## Práctica (2.3 y 2.5)
Archivo: [`practica_02.py`](practica_02.py). Ejecútalo así:

```bash
python docs/practica_02.py
```

El script implementa la neurona de McCulloch-Pitts y el perceptrón, y comprueba que:
- el perceptrón aprende AND y OR;
- el perceptrón **no** logra aprender XOR.

### Ejercicios
1. ¿Qué umbral necesita una neurona de McCulloch-Pitts de 3 entradas para que se active con "al menos 2 de 3"?
2. Cambia `eta` a 0.01 y a 1. ¿Cambia el número de épocas que tarda en converger AND?
3. Imprime `w` y `b` aprendidos para OR y dibuja la recta w₁x₁ + w₂x₂ + b = 0 junto a los 4 puntos.
