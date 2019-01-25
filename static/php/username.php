<?php
            session_start(); // Right at the top of your script
            ?>
            <li class='active' style='float:right;'>
              <?php
              if($_SESSION['logged']==true)
                {
                  echo $_SESSION["username"];
                }
              ?>