import numpy as np


class Rewarder():

    def __init__(self,
                 collect_bomb=0.1,
                 collect_kick=0.1,
                 collect_range=0.1,
                 dead_enemy=0.5,
                 dead_teammate=-0.5,
                 elim_enemy=0.5,
                 elim_teammate=-0.5,
                 explode_crate=0.01,
                 bomb_offset=True):

        self.collect_bomb = collect_bomb
        self.collect_kick = collect_kick
        self.collect_range = collect_range
        self.dead_enemy = dead_enemy
        self.dead_teammate = dead_teammate
        self.elim_enemy = elim_enemy
        self.explode_crate = explode_crate
        self.elim_teammate = elim_teammate
        self.bomb_offset = bomb_offset

    def __call__(self, rewards, board, prev_board, agents, prev_kick, bombs, flames):
        for idx, agent in enumerate(agents):
            if self.bomb_offset:
                # reward = [[-1, rewards[idx]]]
                reward = [[-1, 0]]
            else:
                # reward = rewards[idx]
                reward = 0
            if not agent.is_alive:
                if self.bomb_offset:
                    reward = [[-1, -1]]
                else:
                    reward = -1
                    continue

            if self.collect_bomb:
                reward += self.calc_collect_bomb(
                    agent.position,
                    prev_board)
            if self.collect_kick:
                reward += self.calc_collect_kick(
                    agent.position,
                    prev_board, prev_kick[idx])
            if self.collect_range:
                reward += self.calc_collect_range(
                    agent.position,
                    prev_board)
            if self.dead_enemy:
                reward += self.calc_dead_enemy(
                    [enemy.value for enemy in agent.enemies],
                    board, prev_board, flames)
            if self.dead_teammate:
                reward += self.calc_dead_teammate(
                    agent.teammate.value,
                    board, prev_board, flames)
            if self.elim_enemy:
                reward += self.calc_elim_enemy(
                    agent,
                    [enemy.value for enemy in agent.enemies],
                    board, prev_board, flames)
            if self.explode_crate:
                reward += self.calc_explode_crate(
                    agent, prev_board, flames)
            if self.elim_teammate:
                reward += self.calc_elim_teammate(
                    agent,
                    agent.teammate.value,
                    board, prev_board, flames)
            reward = np.array(reward)
            reward = [[idx, reward[:, 1][reward[:, 0] == idx].sum()]
                      for idx in np.unique(reward[:, 0])]
            reward = np.array(reward)
            reward = reward[np.argsort(reward[:, 0])][::-1]
            rewards[idx] = reward

        return rewards

    def calc_collect_bomb(self, pos, prev_board):
        if prev_board[pos] == 6:
            if self.bomb_offset:
                return [[-1, self.collect_bomb]]
            return self.collect_bomb
        if self.bomb_offset:
            return []
        return 0

    def calc_collect_kick(self, pos, prev_board, kick):
        if (prev_board[pos] == 8) and not kick:
            if self.bomb_offset:
                return [[-1, self.collect_kick]]
            return self.collect_kick
        if self.bomb_offset:
            return []
        return 0

    def calc_collect_range(self, pos, prev_board):
        if prev_board[pos] == 7:
            if self.bomb_offset:
                return [[-1, self.collect_range]]
            return self.collect_range
        if self.bomb_offset:
            return []
        return 0

    def calc_dead_enemy(self, enemies, board, prev_board, flames):
        enemy_dead = sum(
            [(prev_board == enemy) * int(enemy not in board) for enemy in enemies])
        if self.bomb_offset:
            reward = []
        else:
            reward = 0
        if not enemy_dead.any():
            return reward
        enemy_pos = np.where(enemy_dead.astype(bool))
        for pos in zip(*enemy_pos):
            for flame in flames:
                if flame.position == pos:
                    if self.bomb_offset:
                        reward += [[-(12 - flame.life), self.dead_enemy]]
                    else:
                        reward += self.dead_enemy
                    break
        return reward

    def calc_dead_teammate(self, teammate, board, prev_board, flames):
        teammate_dead = (prev_board == teammate) * int(teammate not in board)
        if self.bomb_offset:
            reward = []
        else:
            reward = 0
        if not teammate_dead.any():
            return reward
        teammate_pos = np.where(teammate_dead.astype(bool))
        for pos in zip(*teammate_pos):
            for flame in flames:
                if flame.position == pos:
                    if self.bomb_offset:
                        reward += [[-(12 - flame.life), self.dead_teammate]]
                    else:
                        reward += self.dead_teammate
                    break
        return reward

    def calc_elim_enemy(self, agent, enemies, board, prev_board, flames):
        enemy_dead = sum(
            [(prev_board == enemy) * int(enemy not in board) for enemy in enemies])
        if self.bomb_offset:
            reward = []
        else:
            reward = 0
        if not enemy_dead.any():
            return reward
        enemy_pos = np.where(enemy_dead.astype(bool))
        for pos in zip(*enemy_pos):
            for flame in flames:
                if agent.agent_id != flame.bomber:
                    continue
                if flame.position == pos:
                    if self.bomb_offset:
                        reward += [[-(12 - flame.life), self.elim_enemy]]
                    else:
                        reward += self.elim_enemy
                    break
        return reward

    def calc_elim_teamate(self, agent, teammate, board, prev_board, flames):
        teammate_dead = (prev_board == teammate) * int(teammate not in board)
        if self.bomb_offset:
            reward = []
        else:
            reward = 0
        if not teammate_dead.any():
            return reward
        teammate_pos = np.where(teammate_dead.astype(bool))
        for pos in zip(*teammate_pos):
            for flame in flames:
                if agent.agent_id != flame.bomber:
                    continue
                if flame.position == pos:
                    if self.bomb_offset:
                        reward += [[-(12 - flame.life), self.elim_teammate]]
                    else:
                        reward += self.elim_teammate
                    break
        return reward

    def calc_explode_crate(self, agent, prev_board, flames):
        if self.bomb_offset:
            reward = []
        else:
            reward = 0
        prev_board = prev_board.copy()
        for flame in flames:
            if flame.life < 2 or agent.agent_id != flame.bomber:
                continue
            if prev_board[flame.position] == 2:
                if self.bomb_offset:
                    reward += [[-10, self.explode_crate]]
                else:
                    reward += self.explode_crate
                prev_board[flame.position] = 0
        return reward
