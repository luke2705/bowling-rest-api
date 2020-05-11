from django.core.exceptions import ValidationError

def ball_validator(value):
    stack = []
    frame_count = 0
    bonus_balls = 0
    for char in value:
        if char not in "0123456789/xX":
            raise ValidationError(
                (f'{char} is not a valid ball value')
            )

        if char in '0123456789':
            stack.append(int(char))
            if len(stack)==2:
                if sum(stack)>9:
                    raise ValidationError(
                        (f'consecutive numeric balls, {stack[0]} and {stack[1]}, have sum greater than nine in a single frame')
                    )
                stack = []
                frame_count += 1

        if char == '/':
            if len(stack)==0:
                raise ValidationError(
                    (f'cannot bowl a spare on the first ball of a new frame')
                )
            else:
                stack = []
                frame_count += 1
                if frame_count == 10:
                    bonus_balls = 1

        if char in 'xX':
            if len(stack)==1:
                raise ValidationError(
                    (f'cannot bowl a strike on the second ball of a new frame')
                )
            else:
                frame_count += 1
                if frame_count == 10:
                    bonus_balls = 2
        
        if frame_count >= 10:
            if bonus_balls < 0:
                raise ValidationError(
                    (f'ball was reported after game has already ended')
                )
            bonus_balls -=1

    return value