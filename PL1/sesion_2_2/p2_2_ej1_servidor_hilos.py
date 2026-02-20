hilo = threarding.Thread(target=hoal()) (si pones () no ejecuta la funcion (mete en target lo q retorna y si no retorna
nada retorna none))
% con esto sobreescribimos el hilo (en este caso da igual)
for i in range(5):
    hilo = threarding.Thread(target=hoal)
    hilo.start() 

print("Hilos lanzados")

def hola(quien):
    time.sleep(2)
    print("Hola ", quien)

personas = ["Ana", "Luis", "Pedro", "Maria", "Jorge"]
for per in range personas:
    hilo = threarding.Thread(target=hola, args=(per,))
