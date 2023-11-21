# Description
Automate repetitive tasks by recording a series of actions and playing them back automatically.
<details>
  <summary>Record file can be easily edited.</summary>

>Example or record file lines:   
`M-	573	59	(4, 2, 0)	50`  
`K+	<13>	500`    
>-  `M`,`K` - mouse or keyboard action.
>-  `+`,`-` - press or release action.
>- `573	59` - coordinates of the mouse position on the screen.
>- `(4, 2, 0)`,`<13>` - button/keys codes. Left mouse button and enter key.
>- `500`,`50` - time delay BEFORE taking action in milliseconds.
</details>


# Setup

1. Clone repo
2. `py -m pip install -r requirements.txt`

# Launching

`py main.py {record_file_name} {-execute|-record} {-time|-time N} {-loop M}`

- `record_file_name` - filename or path to file. In `record` mode file will be created.
- `-record` - create a marco of mouse and keyboard press/release events.
- `-execute` - run a marco.
- `-time`|`-time N`
  - in `record` mode `-time` flag activate recording the time between events
  - in `execute` mode `-time N` indicates how many times faster to play the macro. If `N` is `0`, times faster = infinity 
- `-loop M`.
  - in `execute` mode indicates how many times repeat marco. If `M` is `0`, repeats endlessly.

## Afterword
For automation, I haven't found a suitable macro recording
program that I trust. So I decided to write a simple and easy
to use open source program so that everyone can make sure that
it does not contain harmful code.

There are some bugs at the moment:
1. works only for windows
2. display scale specifies different coordinate systems for recording and running macros
3. executing on speed much more than 1 may cause incorrect keyboard input
