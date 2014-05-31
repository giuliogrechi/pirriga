
<html>
<body>

<?
    date_default_timezone_set("Europe/Rome");

    $file =          '/var/www/files_test/program.txt';
    $data =          date("D d M y H:i:s");
    $numerovalvola = $_POST['numerovalvola'];
    $onoff =         $_POST['onoff'];
    $ora    =        $_POST['ora'];
    $minuti =        $_POST['minuti'];
    $durataore    =  $_POST['durataore'];
    $durataminuti =  $_POST['durataminuti'];
    $days = "";
    if ($_POST['lun'] == "si"){$days .= "lunedi,";}
    if ($_POST['mar'] == "si"){$days .= "martedi,";}
    if ($_POST['mer'] == "si"){$days .= "mercoledi,";}
    if ($_POST['gio'] == "si"){$days .= "giovedi,";}
    if ($_POST['ven'] == "si"){$days .= "venerdi,";}
    if ($_POST['sab'] == "si"){$days .= "sabato,";}
    if ($_POST['dom'] == "si"){$days .= "domenica";}

    echo 'Ora:       '.               $data ."<br>";
    echo "<br>";
    echo "numero valvola impostata:". $numerovalvola. "<br>";
    echo "accensione: ".              $onoff. "<br>";
    echo "ora impostata: ".           $ora. ":". $minuti. "<br>";
    echo "durata impostata: ".        $durataore. " ore ". $durataminuti. " minuti <br>";
    echo "giorni impostati: ".        $days. "<br>";
    $line = $data. ",". $onoff. ",". $ora. ",". $minuti. ",". $durataore. ",". $durataminuti. ",". $days;

    $lines = array();
    $fl = fopen($file,"r");
    $lock0 = flock($fl, LOCK_SH);
    if(!$lock0){
        echo $lock0;
        echo "errore nel lock!";
    }
    else{
        while(! feof($fl))
          {
          $lines[] = trim(fgets($fl));
          }

        flock($fl,LOCK_UN);
    }
    fclose($fl);
    echo "<br>";
    for ($i = 0; $i < 4; $i++){
        if ($numerovalvola == $i){
            echo "<br>----> ";
        }
        else{
            echo "<br>";
        }
        echo "valvola ". $i. ": ". $lines[$i];
        }

    $lines[$numerovalvola] = $line;

    $program = fopen($file, 'w');
    $lock = flock($program, LOCK_EX);
    if(!$lock){
        echo $lock;
        echo "errore nel lock!";
    }
    else{
        for ($i = 0; $i < 4; $i++){
            fwrite($program, $lines[$i]. PHP_EOL);
        }
        echo "<br><br>Scritto ($line) nel file";
        flock($program,LOCK_UN);

    }
    fclose($program);
    echo "<br><br>";
    echo "nuova impostazione:";
    for ($i = 0; $i < 4; $i++){
        if ($numerovalvola == $i){
            echo "<br>----> ";
        }
        else{
            echo "<br>";
        }
        echo "valvola ". $i. ": ". $lines[$i];
        }

    sleep(1); #per prendere l'ultima riga aggiornata
    $filelog = "/home/pi/pirrigami/log.txt";
    $lastlog = array();
    $flog = fopen($filelog,"r");
    $lock1 = flock($flog, LOCK_SH);
    if(!$lock1){
        echo $lock1;
        echo "errore nel lock!";
    }
    else{
        while(! feof($flog))
          {
          $lastlog[] = trim(fgets($flog));
          }

        flock($flog,LOCK_UN);
    }
    fclose($flog);
    echo "<br>";
    echo "<br>";
    $last = count($lastlog) - 2;
    echo $lastlog[$last];
    echo $lastlog[$last + 1];
    echo '<br>'.$data;
?><br>
</body>
</html>

