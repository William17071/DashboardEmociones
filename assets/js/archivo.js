document.addEventListener('DOMContentLoaded', function() {
    console.log('Documento cargado y listo');
    
    // Ruta del archivo CSV
    const csvFilePath = '/data/transcripciones.csv'; // Ajusta esta ruta a la ubicación de tu archivo CSV
    console.log('Cargando archivo CSV desde:', csvFilePath);

    function actualizarBarraYTexto(elementId, porcentaje) {
        const elemento = document.getElementById(elementId);
        if (!isNaN(porcentaje) && porcentaje >= 0) {
          elemento.style.width = `${porcentaje}%`;
          elemento.setAttribute('aria-valuenow', porcentaje);
        } else {
          elemento.style.width = '0%';
          elemento.setAttribute('aria-valuenow', 0);
        }
      }

      function obtenerFraseAleatoriaPorEmocion(data, emocion) {
        const frasesFiltradas = data.filter(row => row.emocion === emocion).map(row => row.frase);
        if (frasesFiltradas.length === 0) {
          return 'No hay frases disponibles para esta emoción.';
        }
        const indiceAleatorio = Math.floor(Math.random() * frasesFiltradas.length);
        return frasesFiltradas[indiceAleatorio];
      }
  
    // Función para cargar y procesar el archivo CSV
    async function loadCSV(filePath) {
      try {
        console.log('Iniciando fetch...');
        const response = await fetch(filePath);
        console.log('Estado de la respuesta:', response.status);
        
        if (!response.ok) {
          throw new Error('Network response was not ok: ' + response.statusText);
        }
        
        const csvText = await response.text();
        console.log('Contenido del CSV:', csvText);
        
        Papa.parse(csvText, {
          header: true,
          complete: function(results) {
            console.log('Resultados del parseo:', results);
            const data = results.data;
  
            // Contar registros por clasificación de audio 
            const counts = data.reduce((acc, row) => {
              const idAudio = row.idAudio;
              if (!acc[idAudio]) {
                acc[idAudio] = 0;
              }
              acc[idAudio]++;
              return acc;
            }, {});

            /*console.log('Conteo por idAudio:', counts);*/

              // Mostrar total registros Audios
              const totalRegistrosElement = document.getElementById('total-registros-audios');
              totalRegistrosElement.textContent = Object.keys(counts).length;

              

              // total de registros en el CSV
              const totalRegistros = data.length;
              document.getElementById('total-frases').textContent = `${totalRegistros}`;

              // Contar registros por columna 'emocion'
              const totalFeliz = data.filter(row => row.emocion === 'Feliz').length;
              const totalNeutro = data.filter(row => row.emocion === 'Neutral').length;
              const totalFuria = data.filter(row => row.emocion === 'Enojado').length;
              const totalNoIdent = data.filter(row => row.emocion !== 'Feliz' && row.emocion !== 'Enojado' && row.emocion !== 'Neutral').length;
                          
              // Mostrar numero de resultados por cada emoción
              const totalRegistrosElement2 = document.getElementById('total-registros-neutral');
              totalRegistrosElement2.textContent = totalNeutro;

              const totalRegistrosElement3 = document.getElementById('total-registros-feliz');
              totalRegistrosElement3.textContent = totalFeliz;

              const totalRegistrosElement4 = document.getElementById('total-registros-enojado');
              totalRegistrosElement4.textContent = totalFuria;

              const totalRegistrosElement5 = document.getElementById('total-registros-NoIdent');
              totalRegistrosElement5.textContent = totalNoIdent;

              //Mostrar barra y porcetanje segiun cada emoción

              const porcentajeNeutral = (totalNeutro / totalRegistros * 100).toFixed(1);
              actualizarBarraYTexto('progress-neutral', porcentajeNeutral);
              document.getElementById('porcentaje-neutral').textContent = `${porcentajeNeutral}%`;
              
              const porcentajeFeliz = (totalFeliz / totalRegistros * 100).toFixed(1);
              actualizarBarraYTexto('progress-feliz', porcentajeFeliz);
              document.getElementById('porcentaje-feliz').textContent = `${porcentajeFeliz}%`;

              const porcentajeEnojado = (totalFuria / totalRegistros * 100).toFixed(1);
              actualizarBarraYTexto('progress-enojado', porcentajeEnojado);
              document.getElementById('porcentaje-enojado').textContent = `${porcentajeEnojado}%`;
              
              const porcentajeNoidentificado= (totalNoIdent / totalRegistros * 100).toFixed(1);
              actualizarBarraYTexto('progress-NoIdent', porcentajeNoidentificado);
              document.getElementById('porcentaje-noIdent').textContent = `${porcentajeNoidentificado}%`;


              // Frases Aleaotarias segun categoria
              const fraseAleatoriaNeutral = obtenerFraseAleatoriaPorEmocion(data, 'Neutral');
              document.getElementById('frase-aleatoria-neutral').textContent = fraseAleatoriaNeutral;

              const fraseAleatoriafeliz = obtenerFraseAleatoriaPorEmocion(data, 'Feliz');
              document.getElementById('frase-aleatoria-feliz').textContent = fraseAleatoriafeliz;

              const fraseAleatoriaEnojado = obtenerFraseAleatoriaPorEmocion(data, 'Enojado');
              document.getElementById('frase-aleatoria-enojado').textContent = fraseAleatoriaEnojado;
     
              const fraseAleatoriaNoIdentificadas= obtenerFraseAleatoriaPorEmocion(data, '');
              document.getElementById('frase-aleatoria-NoIdent').textContent = fraseAleatoriaNoIdentificadas;

    
          },
          error: function(error) {
            console.error('Error al parsear el CSV:', error);
          }
        });
        
      } catch (error) {
        console.error('Error al cargar el CSV:', error);
      }
    }
    // Función para refrescar la página automáticamente
    function refrescarPagina() {
        loadCSV(csvFilePath);
    }
    // Cargar el archivo CSV cuando el documento esté listo
    loadCSV(csvFilePath);
    setInterval(refrescarPagina, 3000);
  });
  