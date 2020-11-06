      IDENTIFICATION DIVISION.
      PROGRAM-ID. HELLO.

      ENVIRONMENT DIVISION.
         INPUT-OUTPUT SECTION.
         FILE-CONTROL.
           SELECT RESPONSE ASSIGN TO OUT-FILE
           ORGANIZATION IS LINE SEQUENTIAL
           ACCESS MODE IS SEQUENTIAL
           FILE STATUS WS-RES-STATUS.

      DATA DIVISION.
       FILE SECTION.
       FD RESPONSE.
       01 RESLINE PIC X(512).

         WORKING-STORAGE SECTION.
       01 WS-EOF PIC A(1)  VALUE "N".
       01 WS-HEADER.
             05 HEADER-KEY PIC X(32).
             05 HEADER-VALUE PIC X(32).
       01 WS-REQUEST.
           05 REQUEST-METHOD PIC X(10).
           05 REQUEST-LOCATION PIC X(32).
           05 REQUEST-PROTO PIC X(10).
       01 WS-LOCATION-LEN PIC 9(8) VALUE 0.
       01 WS-INDEX-STR PIC X(10) VALUE "index.html".

       01 WS-RES-STATUS   PIC X(2).
           88 WS-RES-ALREADY-OPEN   VALUE '41'.
       01 WS-REQ-LINE PIC X(2048).
       01 EOF PIC X(1) VALUE X"1A".
       01 CR PIC X(1) VALUE X"0D".

      PROCEDURE DIVISION.
       GO TO READ-IN.
       STOP RUN.

       READ-IN.
           ACCEPT WS-REQ-LINE.
           IF WS-REQ-LINE IS NOT EQUAL TO EOF
               THEN UNSTRING WS-REQ-LINE DELIMITED BY SPACE
                    INTO REQUEST-METHOD, REQUEST-LOCATION, REQUEST-PROTO
                    END-UNSTRING
               ELSE GO TO PARSE-REQ
           END-IF.

       LOOP.
           ACCEPT WS-REQ-LINE.
           IF WS-REQ-LINE IS NOT EQUAL TO CR
               THEN UNSTRING WS-REQ-LINE DELIMITED BY SPACE
                    INTO HEADER-KEY, HEADER-VALUE END-UNSTRING
               ELSE GO TO PARSE-REQ
           END-IF.
           GO TO LOOP.

       PARSE-REQ.
           INSPECT REQUEST-LOCATION
           TALLYING WS-LOCATION-LEN FOR ALL CHARACTERS BEFORE SPACE.

           IF WS-LOCATION-LEN=1 THEN
               MOVE WS-INDEX-STR TO OUT-FILE
           ELSE
               MOVE REQUEST-LOCATION(2:WS-LOCATION-LEN - 1)
               TO OUT-FILE
           END-IF.

           OPEN INPUT RESPONSE.
           IF WS-RES-STATUS <> '00' THEN
               DISPLAY "YEET FILE NOT FOUND"
               GO TO PROG-END
           END-IF

           DISPLAY "HTTP/1.1 200 OK" CR.
           IF OUT-FILE="css/styles.css"
               DISPLAY "Content-Type: text/css" CR
           ELSE
               DISPLAY "Content-Type: text/html" CR
           END-IF.
           DISPLAY "Connection: close" CR.
           DISPLAY CR.
           DISPLAY CR.

           MOVE 'N' TO WS-EOF.
           PERFORM UNTIL WS-EOF='Y'
               READ RESPONSE INTO RESLINE
                   AT END MOVE 'Y' TO WS-EOF
                   NOT AT END DISPLAY RESLINE WITH NO ADVANCING
               END-READ
           END-PERFORM.

       PROG-END.
           CLOSE RESPONSE.

