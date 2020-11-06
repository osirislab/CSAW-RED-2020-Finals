      IDENTIFICATION DIVISION.
      PROGRAM-ID. HELLO.

      ENVIRONMENT DIVISION.
         INPUT-OUTPUT SECTION.
         FILE-CONTROL.
           SELECT REQUEST ASSIGN TO IN-FILE
           ORGANIZATION IS LINE SEQUENTIAL
           ACCESS MODE IS SEQUENTIAL.

           SELECT RESPONSE ASSIGN TO OUT-FILE
           ORGANIZATION IS LINE SEQUENTIAL
           ACCESS MODE IS SEQUENTIAL
           FILE STATUS RES-STATUS.

      DATA DIVISION.
       FILE SECTION.
       FD REQUEST.
       01 REQLINE PIC X(128).

       FD RESPONSE.
       01 RESLINE PIC X(10).

         WORKING-STORAGE SECTION.
       01    WS-EOF PIC A(1)  VALUE "N".
       01 WS-HEADER.
             05 HEADER-KEY PIC X(32).
             05 HEADER-VALUE PIC X(32).
       01 WS-REQUEST.
           05 REQUEST-METHOD PIC X(10).
           05 REQUEST-LOCATION PIC X(10).
           05 REQUEST-PROTO PIC X(10).
       01 LOCATION-LEN PIC 9(1).
       01 INDEX-STR PIC X(10) VALUE "index.html".

       01 RES-STATUS   PIC X(2).
           88 RES-ALREADY-OPEN   VALUE '41'.
       01 REQ-LINE PIC X(32).
       01 EOF PIC X(1) VALUE X"1A".

      PROCEDURE DIVISION.
       MOVE '/dev/tty' TO IN-FILE.
       GO TO READ-IN.
       STOP RUN.

       READ-IN.
           ACCEPT REQ-LINE.
           IF REQ-LINE IS NOT EQUAL TO EOF
               THEN GO TO PARSE-REQ
               ELSE UNSTRING REQLINE DELIMITED BY SPACE
                   INTO REQUEST-METHOD, REQUEST-LOCATION, REQUEST-PROTO
               END-UNSTRING
           END-IF.

       LOOP.
           ACCEPT REQ-LINE.
           DISPLAY REQ-LINE.
           IF REQ-LINE IS NOT EQUAL TO EOF
               THEN GO TO PARSE-REQ
               ELSE UNSTRING REQLINE DELIMITED BY SPACE
                   INTO HEADER-KEY, HEADER-VALUE END-UNSTRING
           END-IF.
           GO TO LOOP.

       PARSE-REQ.
           *> OPEN INPUT REQUEST.
           *> READ REQUEST INTO REQLINE
           *>     NOT AT END UNSTRING REQLINE DELIMITED BY SPACE
           *>         INTO REQUEST-METHOD, REQUEST-LOCATION, REQUEST-PROTO
           *>         END-UNSTRING
           *> END-READ

           *> PERFORM UNTIL WS-EOF='Y'
           *>     READ REQUEST INTO REQLINE
           *>         AT END MOVE 'Y' TO WS-EOF
           *>         NOT AT END UNSTRING REQLINE DELIMITED BY SPACE
           *>             INTO HEADER-KEY, HEADER-VALUE
           *>     END-READ
           *> END-PERFORM.
           *> CLOSE REQUEST.

           *> DISPLAY "METHOD: " REQUEST-METHOD.
           *> DISPLAY "LOCATION: " REQUEST-LOCATION.
           *> DISPLAY "PROTO: " REQUEST-PROTO.
           *> DISPLAY "KEY: " HEADER-KEY.
           *> DISPLAY "VALUE: " HEADER-VALUE.

           UNSTRING REQUEST-LOCATION DELIMITED BY '/'
           INTO REQUEST-LOCATION.

           INSPECT REQUEST-LOCATION
           TALLYING LOCATION-LEN FOR ALL CHARACTERS.

           IF LOCATION-LEN=0 THEN
               STRING REQUEST-LOCATION DELIMITED BY SPACE
               INDEX-STR DELIMITED BY SIZE
               INTO REQUEST-LOCATION
               END-STRING
           END-IF.

           *> DISPLAY "LOC: " REQUEST-LOCATION.
           *> DISPLAY "LEN: " LOCATION-LEN.

           MOVE REQUEST-LOCATION TO OUT-FILE.

           OPEN INPUT RESPONSE.
           IF RES-STATUS <> '00' THEN
               DISPLAY "YEET TABLE NOT FOUND"
               EXIT
           END-IF

           DISPLAY "HTTP/1.1 200 OK" X"0D".
           DISPLAY "Content-Type: text/html" X"0D".
           DISPLAY "Connection: close" X"0D".
           DISPLAY X"0D".
           DISPLAY X"0D".

           MOVE 'N' TO WS-EOF.
           PERFORM UNTIL WS-EOF='Y'
               READ RESPONSE INTO RESLINE
                   AT END MOVE 'Y' TO WS-EOF
                   NOT AT END DISPLAY RESLINE X"0D"
               END-READ
           END-PERFORM.

           CLOSE RESPONSE.

